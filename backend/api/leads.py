import os
import pandas as pd
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body

router = APIRouter()

# Setup correct absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEADS_CSV = os.path.join(DATA_DIR, "Leads_Data.csv")

def _load_leads_df(batch_id: Optional[str] = None):
    """Load the leads DataFrame, optionally constrained to a specific batch."""
    target_csv = LEADS_CSV
    
    if batch_id:
        batch_dir = os.path.join(DATA_DIR, "batches", batch_id)
        batch_csv = os.path.join(batch_dir, "Leads_Data.csv")
        if os.path.exists(batch_csv):
            target_csv = batch_csv
            
    if not os.path.exists(target_csv):
        raise HTTPException(status_code=404, detail="Leads data not found")
        
    df = pd.read_csv(target_csv)
    # Drop unnamed index columns
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    return df

@router.get("")
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    region: Optional[str] = None,
    lead_source: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_dir: str = Query("asc", regex="^(asc|desc)$"),
    batch_id: Optional[str] = None,
):
    """List leads with pagination, search, and filtering."""
    df = _load_leads_df(batch_id)
    
    # 1) Search filter
    if search:
        search = search.lower()
        search_mask = (
            df['name'].str.lower().str.contains(search, na=False) |
            df['company'].str.lower().str.contains(search, na=False) |
            df['title'].str.lower().str.contains(search, na=False)
        )
        df = df[search_mask]
        
    # 2) Specific filters
    if region:
        df = df[df['region'].str.lower() == region.lower()]
    if lead_source:
        df = df[df['lead_source'].str.lower() == lead_source.lower()]
        
    # 3) Sorting
    if sort_by and sort_by in df.columns:
        ascending = sort_dir == "asc"
        df = df.sort_values(by=sort_by, ascending=ascending)
        
    # 4) Pagination
    total = len(df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated = df.iloc[start_idx:end_idx].copy()
    paginated = paginated.where(pd.notnull(paginated), None)
    
    leads_list = paginated.to_dict(orient="records")
    
    return {
        "data": leads_list,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/stats")
def lead_stats(batch_id: Optional[str] = None):
    df = _load_leads_df(batch_id)
    total_leads = len(df)
    active_pursuits = len(df[df['status'].isin(['Analysis', 'Processing_'])])
    
    converted_mask = df['converted'] == True
    conversion_rate = 0
    if total_leads > 0:
        conversion_rate = round((len(df[converted_mask]) / total_leads) * 100, 1)
        
    return {
        "total": total_leads,
        "active_pursuits": active_pursuits,
        "conversion_rate": conversion_rate,
        "ready": len(df[df['status'] == 'Ready'])
    }

@router.get("/filters")
def lead_filters(batch_id: Optional[str] = None):
    df = _load_leads_df(batch_id)
    regions = df['region'].dropna().unique().tolist()
    sources = df['lead_source'].dropna().unique().tolist()
    # Filter out nan/None just in case
    regions = [r for r in regions if r]
    sources = [s for s in sources if s]
    
    return {
        "regions": sorted(regions),
        "lead_sources": sorted(sources)
    }

@router.get("/{record_id}")
def get_lead_details(record_id: str, batch_id: Optional[str] = None):
    """Retrieve full intelligence report data for a specific lead."""
    df = _load_leads_df(batch_id)
    
    if 'record_id' not in df.columns:
        df['record_id'] = df.index.astype(str)
        
    if record_id in df['record_id'].values:
        idx = df[df['record_id'] == record_id].index[0]
    elif 'lead_id' in df.columns and record_id in df['lead_id'].values:
        idx = df[df['lead_id'] == record_id].index[0]
    else:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    row = df.loc[idx].where(pd.notnull(df.loc[idx]), None).to_dict()
    
    import json
    # Map CSV fields into the deeply nested Intelligence Report schema
    lead_id = row.get('lead_id') or str(idx)
    name = row.get('name') or row.get('first_name') or "Unknown"
    company = row.get('company') or row.get('organization') or "Unknown"
    title = row.get('title', "Unknown")
    
    # Default Mock / Fallback Values
    email_draft = [
        {"type": "text", "content": f"Hi {name.split(' ')[0]},"},
        {"type": "br"},
        {"type": "text", "content": "I noticed your recent activity..."}
    ]
    email_subject = "Checking in"
    personalization_factors = []
    research_signals = ["High Engagement", "Target Account Hit"]
    intent_reasoning = f"Based on {row.get('visits', 0)} visits and {row.get('pages_per_visit', 0)} pages/visit."
    intent_recommendation = {"next_best_action": "Pending analysis", "urgency": "Medium"}
    timing_rec = "Tuesday 10:00 AM"
    timing_reason = "High probability of engagement based on historical activity."
    optimal_time_window = "N/A"
    approach = {"type": "standard", "urgency": 50, "content_suggestions": ["Follow up"]}
    engagement_prediction = {"response_probability": 0.0, "expected_delay": 24}
    timeline = {}
    
    from datetime import datetime
    now_str = datetime.now().strftime("%H:%M:%S")
    crm_logs = [
        {"time": now_str, "agent": "SYSTEM", "action": "Initialized lead record.", "status": "INIT"}
    ]
    
    # Attempt to load rich data from the agent outputs directory
    outputs_dir = os.path.join(BASE_DIR, "outputs")
    intel_db_path = os.path.join(outputs_dir, "intel_db.json")
    
    if os.path.exists(intel_db_path):
        try:
            with open(intel_db_path, "r") as f:
                intel_db = json.load(f)
            
            if lead_id in intel_db:
                state = intel_db[lead_id]
                
                # Map research (Agent 1)
                # Ensure each signal is a flat string because frontend expects an array of strings
                if "quality_indicators" in state and isinstance(state["quality_indicators"], list):
                    research_signals = [
                        f"{q.get('metric', '')}: {q.get('value', '')}" if isinstance(q, dict) else str(q)
                        for q in state["quality_indicators"]
                    ]
                
                # Map intent (Agent 2)
                if "key_signals" in state and isinstance(state["key_signals"], list):
                    signals = [s.get("signal", str(s)) if isinstance(s, dict) else str(s) for s in state["key_signals"]]
                    intent_reasoning = " \u2022 ".join(signals)
                if "intent_recommendation" in state:
                    intent_recommendation = state["intent_recommendation"]
                
                # Map message (Agent 3) - Split into lines and breaks for React rendering
                if "email_preview" in state:
                    raw_text = state["email_preview"]
                    paragraphs = str(raw_text).replace('\\n', '\n').split('\n')
                    draft_blocks = []
                    for line in paragraphs:
                        if line.strip() == "":
                            draft_blocks.append({"type": "br"})
                        else:
                            draft_blocks.append({"type": "text", "content": line})
                    email_draft = draft_blocks
                if "subject" in state:
                    email_subject = state.get("subject", "")
                if "personalization_factors" in state:
                    personalization_factors = state.get("personalization_factors", [])
                
                # Map timing (Agent 4)
                if "timing" in state and isinstance(state["timing"], dict):
                    timing_rec = f"{state['timing'].get('recommended_date', '')} {state['timing'].get('send_time', '')}".strip()
                    timing_reason = state['timing'].get('reasoning', '')
                    optimal_time_window = state['timing'].get('optimal_time_window', '')
                if "approach" in state:
                    approach = state["approach"]
                if "engagement_prediction" in state:
                    engagement_prediction = state["engagement_prediction"]
                if "timeline" in state:
                    timeline = state["timeline"]
                
                # Map logs (Agent 5 - Construct from the state's success)
                if "lead_summary" in state:
                    crm_logs = [
                        {"time": now_str, "agent": "RESEARCH", "action": f"Identified {len(research_signals)} signals.", "status": "SUCCESS"},
                        {"time": now_str, "agent": "INTENT", "action": f"Calculated Intent Score: {state.get('intent_score', 0)}", "status": "SUCCESS"},
                        {"time": now_str, "agent": "STRATEGY", "action": "Draft generated via LangGraph.", "status": "SUCCESS"},
                        {"time": now_str, "agent": "TIMING", "action": f"Analyzed history and targeted {timing_rec}", "status": "SUCCESS"},
                        {"time": now_str, "agent": "SYSTEM", "action": "Graph sequence processing finished.", "status": "SUCCESS"}
                    ]
                    
        except Exception as e:
            print(f"Error loading intel file: {e}")
    
    return {
        "lead_id": lead_id,
        "profile": {
            "name": name,
            "title": title,
            "company": company,
            "linkedin": row.get('linkedin', f"linkedin.com/in/{name.lower().replace(' ', '')}"),
            "website": row.get('website', f"{company.lower().replace(' ', '')}.com"),
            "bio": row.get('bio', f"{title} at {company}. Leading strategic initiatives and growth.")
        },
        "agents": {
            "research": {
                "summary": "Processed via LangGraph Pipeline.",
                "signals": research_signals
            },
            "intent": {
                "score": row.get('intent_score', row.get('intent', 0)),
                "reasoning": intent_reasoning,
                "recommendation": intent_recommendation
            },
            "message": {
                "draft": email_draft,
                "subject": email_subject,
                "personalization_factors": personalization_factors
            },
            "timing": {
                "recommended": timing_rec,
                "recommendedReason": timing_reason,
                "optimal_time_window": optimal_time_window,
                "approach": approach,
                "engagement_prediction": engagement_prediction,
                "timeline": timeline
            },
            "crm": {
                "logs": crm_logs
            }
        },
        "status": row.get('status', 'Ready'),
        "batch_id": batch_id
    }

@router.patch("/{record_id}/status")
def update_lead_status(record_id: str, payload: dict = Body(...)):
    new_status = payload.get("status")
    intent_score = payload.get("intent_score")
    
    if not new_status and intent_score is None:
        raise HTTPException(status_code=400, detail="Missing status or intent_score in body")
        
    df = _load_leads_df()
    
    if 'record_id' not in df.columns:
        df['record_id'] = df.index.astype(str)
        
    # Also support searching by lead_id 
    if record_id in df['record_id'].values:
        idx = df[df['record_id'] == record_id].index[0]
    elif 'lead_id' in df.columns and record_id in df['lead_id'].values:
        idx = df[df['lead_id'] == record_id].index[0]
    else:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if new_status:
        df.at[idx, 'status'] = new_status
    if intent_score is not None:
        df.at[idx, 'intent_score'] = intent_score
        
    df.to_csv(LEADS_CSV, index=False)
    
    # Return updated row
    updated_row = df.loc[idx].where(pd.notnull(df.loc[idx]), None).to_dict()
    return updated_row
