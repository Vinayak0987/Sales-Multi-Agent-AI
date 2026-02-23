"""CRM Logger Node

Creates a final mock log of the lead's entire multi-agent journey and outputs a summary.
"""

from typing import Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END

def create_crm_logger_graph():
    """Create CRM Logger workflow (no LLM required)"""
    workflow = StateGraph(Dict[str, Any])
    
    workflow.add_node("prepare_data", prepare_data)
    workflow.add_node("generate_log", generate_log)
    
    workflow.add_edge("prepare_data", "generate_log")
    workflow.add_edge("generate_log", END)
    
    workflow.set_entry_point("prepare_data")
    return workflow.compile()

def prepare_data(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n=== prepare_data Step (CRM Logger) ===")
    return {
        **state,
        "status": "data_prepared"
    }

def generate_log(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mock the final CRM event log and summarize"""
    print("\n=== generate_log Step ===")
    
    lead = state.get("lead", {})
    email_history = state.get("email_history", [])
    
    # Track the major events that happened in this LangGraph run
    events = ["lead_research_update", "intent_update", "email_strategy_update", "followup_timing_update"]
    
    total_past_emails = len(email_history)
    replies = sum(1 for e in email_history if e.get("replied"))
    response_rate = (replies / total_past_emails) if total_past_emails > 0 else 0.0
    
    lead_summary = {
        "total_events": len(events) + total_past_emails,
        "event_types": events,
        "response_rate": response_rate
    }
    
    now = datetime.now().isoformat()
    timing = state.get("timing", {})
    
    timeline = {
        "first_contact": now,  # In a real DB this would be historical
        "last_contact": now,
        "next_followup": timing.get("recommended_date", None)
    }
    
    return {
        **state,
        "lead_summary": lead_summary,
        "timeline": timeline,
        "status": "completed"
    }
