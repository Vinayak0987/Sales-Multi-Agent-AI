"""Data transformers for different agent event types."""

from typing import Dict, Any
from datetime import datetime

def transform_lead_research_event(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform lead research data into standard event format."""
    return {
        "lead_id": str(lead_data.get("lead_id")),
        "event_type": "lead_research_update",
        "source_agent": "lead_research",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "company_name": lead_data.get("company", ""),
            "industry": lead_data.get("industry", "Technology"),
            "region": lead_data.get("region", ""),
            "behavioral_metrics": {
                "visits": int(lead_data.get("visits", 0)),
                "time_on_site": int(lead_data.get("time_on_site", 0)),
                "pages_per_visit": float(lead_data.get("pages_per_visit", 0))
            }
        }
    }

def transform_intent_event(intent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform intent qualifier data into standard event format."""
    return {
        "lead_id": str(intent_data.get("lead_id")),
        "event_type": "intent_update",
        "source_agent": "intent_qualifier",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "intent_score": float(intent_data.get("intent_score", 0)),
            "signals": intent_data.get("intent_signals", []),
            "recommendations": intent_data.get("recommendations", []),
            "confidence": intent_data.get("confidence_tag", "medium")
        }
    }

def transform_email_event(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform email strategy data into standard event format."""
    return {
        "lead_id": str(email_data.get("lead_id")),
        "event_type": "email_sent",
        "source_agent": "email_strategy",
        "timestamp": email_data.get("sent_time", datetime.now().isoformat()),
        "data": {
            "email_id": str(email_data.get("email_id")),
            "subject": email_data.get("subject", ""),
            "type": email_data.get("email_type", "initial"),
            "reply_status": email_data.get("reply_status", "pending"),
            "engagement": {
                "opened": bool(email_data.get("opened", False)),
                "replied": bool(email_data.get("replied_time") is not None),
                "engagement_score": float(email_data.get("engagement_score", 0))
            }
        }
    }

def transform_followup_event(followup_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform followup timing data into standard event format."""
    return {
        "lead_id": str(followup_data.get("lead_id")),
        "event_type": "followup_scheduled",
        "source_agent": "followup_timing",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "scheduled_time": followup_data.get("scheduled_time", ""),
            "followup_type": followup_data.get("followup_type", "email"),
            "urgency_score": float(followup_data.get("urgency_score", 50)),
            "timing_patterns": followup_data.get("timing_patterns", {
                "best_days": [],
                "best_hours": []
            })
        }
    }
