"""
Leads API — CRUD operations for lead data.
"""

import os
import pandas as pd
from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from typing import Optional
import shutil
import json

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
LEADS_CSV = os.path.join(DATA_DIR, "Leads_Data.csv")


def _load_leads_df():
    """Load the leads DataFrame."""
    if not os.path.exists(LEADS_CSV):
        raise HTTPException(status_code=404, detail="Leads data not found")
    df = pd.read_csv(LEADS_CSV)
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
):
    """List leads with pagination, search, and filtering."""
    df = _load_leads_df()

    # Search
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]

    # Filters
    if region:
        df = df[df["region"].str.contains(region, case=False, na=False)]
    if lead_source:
        df = df[df["lead_source"].str.contains(lead_source, case=False, na=False)]

    # Sorting
    if sort_by and sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=(sort_dir == "asc"))

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = df.iloc[start:end]

    # Convert to records, handling NaN values
    records = json.loads(page_data.to_json(orient="records"))

    return {
        "leads": records,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/stats")
def lead_stats():
    """Get summary statistics about leads."""
    df = _load_leads_df()

    stats = {
        "total_leads": len(df),
        "by_region": df["region"].value_counts().head(10).to_dict() if "region" in df.columns else {},
        "by_source": df["lead_source"].value_counts().head(10).to_dict() if "lead_source" in df.columns else {},
        "converted": int(df["converted"].sum()) if "converted" in df.columns else 0,
        "conversion_rate": float(df["converted"].mean()) if "converted" in df.columns else 0,
    }
    return stats


@router.get("/filters")
def lead_filters():
    """Get available filter values."""
    df = _load_leads_df()

    filters = {
        "regions": sorted(df["region"].dropna().unique().tolist()) if "region" in df.columns else [],
        "sources": sorted(df["lead_source"].dropna().unique().tolist()) if "lead_source" in df.columns else [],
    }
    return filters


@router.get("/{lead_id}")
def get_lead(lead_id: str):
    """Get a single lead by index or lead_id."""
    df = _load_leads_df()

    # Try to find by lead_id column
    if "lead_id" in df.columns:
        match = df[df["lead_id"] == lead_id]
        if not match.empty:
            record = json.loads(match.iloc[0].to_json())
            record["_index"] = int(match.index[0])
            return record

    # Fallback: try numeric index
    try:
        idx = int(lead_id)
        if 0 <= idx < len(df):
            record = json.loads(df.iloc[idx].to_json())
            record["_index"] = idx
            return record
    except ValueError:
        pass

    raise HTTPException(status_code=404, detail=f"Lead '{lead_id}' not found")


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a new leads CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    # Check file size (25MB max)
    contents = await file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 25MB limit")

    # Save file
    dest = os.path.join(DATA_DIR, file.filename)
    with open(dest, "wb") as f:
        f.write(contents)

    # Validate it's valid CSV
    try:
        df = pd.read_csv(dest)
        return {
            "status": "success",
            "filename": file.filename,
            "rows": len(df),
            "columns": df.columns.tolist(),
        }
    except Exception as e:
        os.remove(dest)
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
