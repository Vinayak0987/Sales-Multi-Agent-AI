"""
Agents API — Run and monitor the multi-agent pipeline.
"""

import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")


class AgentRunRequest(BaseModel):
    lead_id: Optional[str] = None
    lead_index: Optional[int] = None
    params: Optional[Dict[str, Any]] = None


# In-memory agent status tracking
_agent_status = {
    "lead_research": {"status": "idle", "last_run": None, "result": None},
    "intent_qualifier": {"status": "idle", "last_run": None, "result": None},
    "email_strategy": {"status": "idle", "last_run": None, "result": None},
    "followup_timing": {"status": "idle", "last_run": None, "result": None},
    "crm_logger": {"status": "idle", "last_run": None, "result": None},
}


@router.get("/status")
def get_agent_status():
    """Get status of all agents in the pipeline."""
    agents = [
        {
            "id": "lead_research",
            "name": "Lead Research Agent",
            "description": "Behavioral pattern analysis & lead segmentation",
            "icon": "search",
            "stage": 1,
            "status": _agent_status["lead_research"]["status"],
            "last_run": _agent_status["lead_research"]["last_run"],
        },
        {
            "id": "intent_qualifier",
            "name": "Intent Qualifier Agent",
            "description": "Evaluates engagement patterns & contextual intent",
            "icon": "target",
            "stage": 2,
            "status": _agent_status["intent_qualifier"]["status"],
            "last_run": _agent_status["intent_qualifier"]["last_run"],
        },
        {
            "id": "email_strategy",
            "name": "Email Strategy Agent",
            "description": "Personalized content creation & success patterns",
            "icon": "mail",
            "stage": 3,
            "status": _agent_status["email_strategy"]["status"],
            "last_run": _agent_status["email_strategy"]["last_run"],
        },
        {
            "id": "followup_timing",
            "name": "Follow-up Timing Agent",
            "description": "Response pattern analysis & engagement timing",
            "icon": "clock",
            "stage": 4,
            "status": _agent_status["followup_timing"]["status"],
            "last_run": _agent_status["followup_timing"]["last_run"],
        },
        {
            "id": "crm_logger",
            "name": "CRM Logger Agent",
            "description": "Records interactions & calculates metrics",
            "icon": "database",
            "stage": 5,
            "status": _agent_status["crm_logger"]["status"],
            "last_run": _agent_status["crm_logger"]["last_run"],
        },
    ]
    return {"agents": agents}


@router.get("/outputs")
def list_outputs():
    """List available pre-computed agent outputs."""
    outputs = []
    if os.path.exists(OUTPUTS_DIR):
        for fname in os.listdir(OUTPUTS_DIR):
            if fname.endswith(".json"):
                fpath = os.path.join(OUTPUTS_DIR, fname)
                stat = os.stat(fpath)
                # Try to load a preview
                try:
                    with open(fpath, "r") as f:
                        data = json.load(f)
                    preview = str(data)[:200] if isinstance(data, (dict, list)) else str(data)[:200]
                except Exception:
                    preview = "Unable to parse"

                outputs.append({
                    "filename": fname,
                    "agent": fname.replace("_output.json", ""),
                    "size_bytes": stat.st_size,
                    "preview": preview,
                })

    return {"outputs": outputs}


@router.get("/outputs/{filename}")
def get_output(filename: str):
    """Get a specific agent output file."""
    fpath = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="Output not found")

    try:
        with open(fpath, "r") as f:
            data = json.load(f)
        return {"filename": filename, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read output: {str(e)}")


@router.post("/run/{agent_id}")
def run_agent(agent_id: str, request: AgentRunRequest):
    """Trigger an agent run (returns pre-computed results for demo)."""
    if agent_id not in _agent_status:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    from datetime import datetime

    # Check if we have pre-computed output
    output_file = os.path.join(OUTPUTS_DIR, f"{agent_id}_output.json")
    result = None
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                result = json.load(f)
        except Exception:
            pass

    # Update status
    _agent_status[agent_id]["status"] = "completed"
    _agent_status[agent_id]["last_run"] = datetime.now().isoformat()
    _agent_status[agent_id]["result"] = result

    return {
        "agent_id": agent_id,
        "status": "completed",
        "timestamp": _agent_status[agent_id]["last_run"],
        "result": result,
    }
