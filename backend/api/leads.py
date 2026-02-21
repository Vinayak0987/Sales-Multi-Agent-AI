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
