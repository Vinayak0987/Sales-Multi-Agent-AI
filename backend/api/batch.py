import os
import io
import time
import json
import pandas as pd
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import Ollama wrapper
from api.agents import OllamaWrapper

# Import our LangGraph node compilers
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from langgraph_nodes.lead_research_node import create_lead_research_graph
from langgraph_nodes.intent_qualifier_node import create_intent_qualifier_graph
from langgraph_nodes.email_strategy_node import create_email_strategy_graph
from langgraph_nodes.followup_timing_node import create_followup_timing_graph
from langgraph_nodes.crm_logger_node import create_crm_logger_graph

from prompts.lead_research_prompts import lead_research_prompts
from prompts.intent_qualifier_prompts import intent_qualifier_prompts
from prompts.email_strategy_prompts import email_strategy_prompts
from prompts.followup_timing_prompts import followup_timing_prompts

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
BATCHES_DIR = os.path.join(DATA_DIR, "batches")
GLOBAL_LEADS_CSV = os.path.join(DATA_DIR, "Leads_Data.csv")

os.makedirs(BATCHES_DIR, exist_ok=True)

def update_batch_progress(batch_id: str, updates: dict):
    """Helper to merge updates into the batch's _progress.json"""
    batch_dir = os.path.join(BATCHES_DIR, batch_id)
    progress_file = os.path.join(batch_dir, "_progress.json")
    
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            data = json.load(f)
    else:
        data = {
            "batch_id": batch_id,
            "status": "processing",
            "percent": 0,
            "processed_count": 0,
            "total_count": 0,
            "agents": {
                "research": "pending",
                "intent": "pending",
                "message": "pending",
                "timing": "pending",
                "logger": "pending"
            }
        }
    
    for key, val in updates.items():
        if key == "agents":
            data["agents"].update(val)
        else:
            data[key] = val
        
    temp_file = progress_file + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=4)
    os.replace(temp_file, progress_file)

@router.get("/{batch_id}/progress")
def get_batch_progress(batch_id: str):
    progress_file = os.path.join(BATCHES_DIR, batch_id, "_progress.json")
    if not os.path.exists(progress_file):
        raise HTTPException(status_code=404, detail="Batch progress not found")
    with open(progress_file, "r") as f:
        return json.load(f)

def process_batch_background(batch_id: str):
    """
    Background worker that uses LangGraph to process each lead sequentially 
    through 5 AI agents, updating the CSV instantly so the UI can stream it.
    """
    try:
        time.sleep(1) # Give the UI a second to process the success response
        
        batch_dir = os.path.join(BATCHES_DIR, batch_id)
        leads_file = os.path.join(batch_dir, "Leads_Data.csv")
        emails_file = os.path.join(batch_dir, "Email_Logs.csv")
        
        if not os.path.exists(leads_file):
            update_batch_progress(batch_id, { "status": "failed", "error": "Leads file missing" })
            return
            
        df = pd.read_csv(leads_file)
        emails_df = pd.read_csv(emails_file) if os.path.exists(emails_file) else pd.DataFrame()
        
        # Load the Ollama LLM
        llm = OllamaWrapper('minimax-m2:cloud')
        
        # Compile the 5 independent LangGraph pipelines
        lead_research_agent = create_lead_research_graph(llm, lead_research_prompts)
        intent_qualifier_agent = create_intent_qualifier_graph(llm, intent_qualifier_prompts)
        email_strategy_agent = create_email_strategy_graph(llm, email_strategy_prompts)
        followup_timing_agent = create_followup_timing_graph(llm, followup_timing_prompts)
        crm_logger_agent = create_crm_logger_graph()
        
        total = len(df)
        
        update_batch_progress(batch_id, {
            "percent": 0,
            "processed_count": 0,
            "total_count": total,
            "agents": { k: "running" for k in ["research", "intent", "message", "timing", "logger"] }
        })
        
        # Stream analytics loop
        file_lock = threading.Lock()
        processed = 0

        def process_lead(index, row):
            nonlocal processed
            lead_dict = row.dropna().to_dict()
            lead_id = lead_dict.get("lead_id", "")
            
            # Extract previous emails for this specific lead to give to the state
            if not emails_df.empty and 'lead_id' in emails_df.columns:
                email_history = emails_df[emails_df['lead_id'] == lead_id].to_dict('records')
            else:
                email_history = []
                
            # Initialize unifying state
            state = {
                "lead": lead_dict,
                "email_history": email_history
            }
            
            print(f"\\n[Processing] Lead {lead_id} ({lead_dict.get('company', 'Unknown')}) through LangGraph pipeline...")
            
            try:
                # Node 1: Lead Research
                state = lead_research_agent.invoke(state)
                # Node 2: Intent Qualifier
                state = intent_qualifier_agent.invoke(state)
                # Node 3: Email Strategy 
                state = email_strategy_agent.invoke(state)
                # Node 4: Followup Timing
                state = followup_timing_agent.invoke(state)
                # Node 5: CRM Logger
                state = crm_logger_agent.invoke(state)
                
                with file_lock:
                    # Success! Extract the outputs into our dataframe for the frontend
                    df.at[index, "status"] = "Ready"
                    df.at[index, "intent_score"] = state.get("intent_score", 0.0)
                    df.at[index, "subject"] = state.get("subject", "")
                    df.at[index, "email_preview"] = state.get("email_preview", "")
                    
                    # Dump the full LangGraph state to an intel payload for the frontend /intel page
                    outputs_dir = os.path.join(root_dir, "outputs")
                    os.makedirs(outputs_dir, exist_ok=True)
                    
                    intel_db_path = os.path.join(outputs_dir, "intel_db.json")
                    intel_db = {}
                    if os.path.exists(intel_db_path):
                        try:
                            with open(intel_db_path, "r") as f:
                                intel_db = json.load(f)
                        except json.JSONDecodeError:
                            pass
                    
                    intel_db[lead_id] = state
                    temp_intel = intel_db_path + ".tmp"
                    with open(temp_intel, "w") as f:
                        json.dump(intel_db, f, indent=4)
                    os.replace(temp_intel, intel_db_path)
                        
                    # Stream this row instantly to the Ledger
                    temp_leads = leads_file + ".tmp"
                    df.to_csv(temp_leads, index=False)
                    os.replace(temp_leads, leads_file)
                    
                    temp_global = GLOBAL_LEADS_CSV + ".tmp"
                    df.to_csv(temp_global, index=False)
                    os.replace(temp_global, GLOBAL_LEADS_CSV)
                
            except Exception as e:
                print(f"Error processing lead {lead_id}: {e}")
                with file_lock:
                    df.at[index, "status"] = "Error"
                    temp_leads = leads_file + ".tmp"
                    df.to_csv(temp_leads, index=False)
                    os.replace(temp_leads, leads_file)
                    
                    temp_global = GLOBAL_LEADS_CSV + ".tmp"
                    df.to_csv(temp_global, index=False)
                    os.replace(temp_global, GLOBAL_LEADS_CSV)
                
            with file_lock:
                # Tick progress
                processed += 1
                percent = int((processed / total) * 100)
                update_batch_progress(batch_id, {
                    "percent": percent,
                    "processed_count": processed,
                    "total_count": total
                })

        # Process all leads concurrently using worker threads
        # Set max_workers=2 to balance parallel execution without overloading the local Ollama instance & locking up the system CPU.
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(process_lead, index, row) for index, row in df.iterrows()]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Future execution error: {e}")
            
        # Finish
        update_batch_progress(batch_id, {
            "status": "completed",
            "percent": 100,
            "processed_count": total,
            "total_count": total,
            "agents": { k: "completed" for k in ["research", "intent", "message", "timing", "logger"] }
        })
        print(f"Batch {batch_id} fully processed through LangGraph and synced to global Ledger mapping.")
                
    except Exception as e:
        print(f"Error during Background Batch processing: {e}")
        update_batch_progress(batch_id, { "status": "failed", "percent": 0 })

@router.post("/upload")
async def upload_batch(
    background_tasks: BackgroundTasks,
    agent_mapping: UploadFile = File(...),
    crm_pipeline: UploadFile = File(...),
    email_logs: UploadFile = File(...),
    leads_data: UploadFile = File(...),
    sales_pipeline: UploadFile = File(...),
):
    try:
        import uuid
        date_str = datetime.now().strftime("%Y_%m_%d")
        short_id = str(uuid.uuid4())[:8].upper()
        batch_id = f"BATCH_{date_str}_{short_id}"
        
        batch_dir = os.path.join(BATCHES_DIR, batch_id)
        os.makedirs(batch_dir, exist_ok=True)
        
        # Helper to read into RAM and dump cleanly to the batch structure
        async def save_file(upload_file: UploadFile, filename: str):
            contents = await upload_file.read()
            df = pd.read_csv(io.BytesIO(contents))
            df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
            df.to_csv(os.path.join(batch_dir, filename), index=False)
            
        await save_file(agent_mapping, "Agent_Mapping.csv")
        await save_file(crm_pipeline, "CRM_Pipeline.csv")
        await save_file(email_logs, "Email_Logs.csv")
        await save_file(leads_data, "Leads_Data.csv")
        await save_file(sales_pipeline, "Sales_Pipeline.csv")
        
        update_batch_progress(batch_id, { "percent": 0 })
        
        background_tasks.add_task(process_batch_background, batch_id)
        
        return {
            "batch_id": batch_id,
            "status": "processing",
            "files_received": 5
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch upload rejected: {str(e)}")
