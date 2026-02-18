"""
Dashboard API — Aggregated stats and activity feed.
"""

import os
import json
import pandas as pd
from fastapi import APIRouter
from datetime import datetime, timedelta
import random

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")


@router.get("/stats")
def dashboard_stats():
    """Get KPI card data for the dashboard."""
    stats = {
        "total_leads": 0,
        "conversion_rate": 0,
        "pipeline_value": 0,
        "active_agents": 5,
        "emails_sent": 0,
        "response_rate": 0,
    }

    # Leads stats
    leads_path = os.path.join(DATA_DIR, "Leads_Data.csv")
    if os.path.exists(leads_path):
        df = pd.read_csv(leads_path)
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
        stats["total_leads"] = len(df)
        if "converted" in df.columns:
            stats["conversion_rate"] = round(float(df["converted"].mean()) * 100, 1)

    # Sales pipeline stats
    pipeline_path = os.path.join(DATA_DIR, "Sales_Pipeline.csv")
    if os.path.exists(pipeline_path):
        df = pd.read_csv(pipeline_path)
        if "close_value" in df.columns:
            stats["pipeline_value"] = int(df["close_value"].sum())

    # Email stats
    email_path = os.path.join(DATA_DIR, "Email_Logs.csv")
    if os.path.exists(email_path):
        df = pd.read_csv(email_path)
        stats["emails_sent"] = len(df)
        if "opened" in df.columns:
            stats["response_rate"] = round(float(df["opened"].mean()) * 100, 1)

    return stats


@router.get("/activity")
def dashboard_activity():
    """Get recent agent activity feed."""
    # Generate activity from actual output files
    activities = []
    now = datetime.now()

    output_files = {
        "lead_research_output.json": {
            "agent": "Lead Research",
            "icon": "search",
            "color": "#52c41a",
        },
        "intent_qualifier_output.json": {
            "agent": "Intent Qualifier",
            "icon": "target",
            "color": "#fa8c16",
        },
        "email_strategy_output.json": {
            "agent": "Email Strategy",
            "icon": "mail",
            "color": "#2f54eb",
        },
        "crm_logger_output.json": {
            "agent": "CRM Logger",
            "icon": "database",
            "color": "#722ed1",
        },
    }

    for fname, meta in output_files.items():
        fpath = os.path.join(OUTPUTS_DIR, fname)
        if os.path.exists(fpath):
            stat = os.stat(fpath)
            activities.append({
                "id": fname,
                "agent": meta["agent"],
                "icon": meta["icon"],
                "color": meta["color"],
                "action": f"{meta['agent']} completed analysis. Output ready ({stat.st_size:,} bytes).",
                "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    # Add simulated recent activities
    simulated = [
        {"agent": "Lead Research", "icon": "search", "color": "#52c41a",
         "action": "Completed deep dive for Nexus Dynamics. Found 3 new articles regarding Series B funding."},
        {"agent": "Intent Qualifier", "icon": "target", "color": "#fa8c16",
         "action": "High intent signal detected. Intent score spiked +15 pts for priority target."},
        {"agent": "Email Strategy", "icon": "mail", "color": "#2f54eb",
         "action": "Drafted outreach sequence based on recent earnings report."},
        {"agent": "CRM Logger", "icon": "database", "color": "#722ed1",
         "action": "Batch upload processed. 15 new leads added to The Ledger."},
        {"agent": "Follow-up Timing", "icon": "clock", "color": "#eb2f96",
         "action": "Scheduled follow-up. Optimal window: Tuesday 14:00."},
        {"agent": "Lead Research", "icon": "search", "color": "#52c41a",
         "action": "Initiating background analysis for Lead List #402."},
    ]

    for i, item in enumerate(simulated):
        activities.append({
            "id": f"sim_{i}",
            "agent": item["agent"],
            "icon": item["icon"],
            "color": item["color"],
            "action": item["action"],
            "timestamp": (now - timedelta(minutes=i * 12 + random.randint(1, 10))).isoformat(),
        })

    # Sort by timestamp descending
    activities.sort(key=lambda x: x["timestamp"], reverse=True)

    return {"activities": activities}


@router.get("/pipeline")
def dashboard_pipeline():
    """Get sales pipeline breakdown."""
    pipeline_path = os.path.join(DATA_DIR, "Sales_Pipeline.csv")
    if not os.path.exists(pipeline_path):
        return {"stages": []}

    df = pd.read_csv(pipeline_path)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    if "deal_stage" not in df.columns:
        return {"stages": []}

    stages = df.groupby("deal_stage").agg(
        count=("deal_stage", "size"),
        value=("close_value", "sum") if "close_value" in df.columns else ("deal_stage", "size"),
    ).reset_index()

    return {
        "stages": json.loads(stages.to_json(orient="records"))
    }


@router.get("/priority-targets")
def priority_targets():
    """Get top priority leads for the dashboard."""
    leads_path = os.path.join(DATA_DIR, "Leads_Data.csv")
    if not os.path.exists(leads_path):
        return {"targets": []}

    df = pd.read_csv(leads_path)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # Pick leads with high activity as priority targets
    score_cols = []
    if "time_on_site" in df.columns:
        score_cols.append("time_on_site")
    if "pages_per_visit" in df.columns:
        score_cols.append("pages_per_visit")
    if "visits" in df.columns:
        score_cols.append("visits")

    if score_cols:
        for col in score_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        df["_score"] = df[score_cols].sum(axis=1)
        df = df.sort_values("_score", ascending=False)

    top = df.head(6)
    records = json.loads(top.to_json(orient="records"))

    # Enrich with fake signals for the dashboard display
    signals = [
        "Viewed pricing page 4x in last 24h",
        "Downloaded Q3 whitepaper",
        "LinkedIn connection accepted",
        "Attended product webinar",
        "Opened 3 emails this week",
        "Visited case studies section",
    ]

    targets = []
    for i, rec in enumerate(records):
        targets.append({
            "index": i,
            "name": rec.get("name", f"Lead {i}"),
            "title": rec.get("title", "Unknown"),
            "company": rec.get("company", "Unknown"),
            "region": rec.get("region", ""),
            "signal": signals[i % len(signals)],
        })

    return {"targets": targets}
