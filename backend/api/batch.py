import os
import io
import time
import json
import pandas as pd
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
import asyncio

from api.agents import analyze_dataset_bulk

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
            "agents": {
                "research": "pending",
                "intent": "pending",
                "message": "pending",
                "timing": "pending",
                "logger": "pending"
            }
        }
    
    if "status" in updates:
        data["status"] = updates["status"]
    if "percent" in updates:
        data["percent"] = updates["percent"]
    if "agents" in updates:
        data["agents"].update(updates["agents"])
        
    with open(progress_file, "w") as f:
        json.dump(data, f, indent=4)

@router.get("/{batch_id}/progress")
def get_batch_progress(batch_id: str):
    progress_file = os.path.join(BATCHES_DIR, batch_id, "_progress.json")
    if not os.path.exists(progress_file):
        raise HTTPException(status_code=404, detail="Batch progress not found")
    with open(progress_file, "r") as f:
        return json.load(f)

def process_batch_background(batch_id: str):
    """
    Background worker that runs immediately after the 5 files are successfully downloaded to disk.
    It prepares the data for the global Ledger lookup, then triggers LangGraph.
    """
    try:
        time.sleep(1) # Give the UI a second to process the success response
        
        # Start Research Agent
        update_batch_progress(batch_id, {
            "percent": 10,
            "agents": { "research": "running" }
        })
        
        batch_dir = os.path.join(BATCHES_DIR, batch_id)
        leads_file = os.path.join(batch_dir, "Leads_Data.csv")
        
        if os.path.exists(leads_file):
            df = pd.read_csv(leads_file)
            
            # Agent Running => Status = Processing_
            df['status'] = 'Processing_'
            
            # We run the Research LangGraph step first now
            try:
                # Trigger the real LangGraph insights engine via bulk
                asyncio.run(analyze_dataset_bulk())
                print(f"Batch {batch_id} fully researched via LangGraph.")
            except Exception as e:
                print(f"Error triggering global agents inside batch: {e}")
                update_batch_progress(batch_id, { "status": "failed", "agents": { "research": "error" } })
                return
                
            # Research done, moving to Intent Scoring
            update_batch_progress(batch_id, {
                "percent": 30,
                "agents": { "research": "completed", "intent": "running" }
            })
            
            time.sleep(1) # simulate scoring time
            
            visits = pd.to_numeric(df['visits'], errors='coerce').fillna(0)
            pages = pd.to_numeric(df['pages_per_visit'], errors='coerce').fillna(0)
            converted = df['converted'].astype(bool).fillna(False)
            
            base_score = pd.Series(40, index=df.index)
            base_score += (visits > 5) * 25 + ((visits <= 5) & (visits > 2)) * 15
            base_score += (pages > 4) * 20
            base_score += converted * 10
            
            df['intent_score'] = base_score.clip(upper=99)
            
            # Save the scored version both in the batch folder and as the new global Leads_Data.csv
            # so the Ledger Page immediately reflects the changes!
            df.to_csv(leads_file, index=False)
            df.to_csv(GLOBAL_LEADS_CSV, index=False)
            print(f"Batch {batch_id} fully scored and synced to global Ledger mapping.")
            
            # Intent done, move to downstream mock agents
            update_batch_progress(batch_id, {
                "percent": 60,
                "agents": { "intent": "completed", "message": "running" }
            })
            time.sleep(1)
            update_batch_progress(batch_id, {
                "percent": 85,
                "agents": { "message": "completed", "timing": "completed", "logger": "running" }
            })
            time.sleep(0.5)
            
            update_batch_progress(batch_id, {
                "status": "completed",
                "percent": 100,
                "agents": { "logger": "completed" }
            })
            
            # Upgrade global leads file to Ready status
            df['status'] = 'Ready'
            df.to_csv(leads_file, index=False)
            df.to_csv(GLOBAL_LEADS_CSV, index=False)
                
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
            # Read cleanly to memory and drop directly to disk without locks
            df = pd.read_csv(io.BytesIO(contents))
            # Clean unseen whitespace/unnamed columns
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
