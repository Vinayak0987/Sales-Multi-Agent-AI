from typing import Dict, List, Any
from datetime import datetime
from .data_transformers import (
    transform_lead_research_event,
    transform_intent_event,
    transform_email_event,
    transform_followup_event
)

class CRMLoggerAgent:
    """CRM Logger Agent for tracking all lead-related events."""
    
    def __init__(self):
        self.leads = {}  # Store lead data
        self.transformers = {
            "lead_research": transform_lead_research_event,
            "intent_qualifier": transform_intent_event,
            "email_strategy": transform_email_event,
            "followup_timing": transform_followup_event
        }
    
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process and store an event."""
        try:
            # Transform event based on source agent
            source_agent = event.get("source_agent")
            if source_agent in self.transformers:
                event = self.transformers[source_agent](event)
            
            # Validate transformed event
            if not self._validate_event(event):
                return {"status": "error", "message": "Invalid event format"}
            
            # Initialize lead if not exists
            lead_id = event["lead_id"]
            if lead_id not in self.leads:
                self.leads[lead_id] = {
                    "events": [],
                    "metrics": self._init_metrics()
                }
            
            # Add timestamp if not present
            if "timestamp" not in event:
                event["timestamp"] = datetime.now().isoformat()
            
            # Store event
            self.leads[lead_id]["events"].append(event)
            
            # Update metrics
            self._update_metrics(lead_id, event)
            
            return {"status": "success", "message": "Event processed"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_lead_history(self, lead_id: str) -> List[Dict]:
        """Get all events for a lead."""
        if lead_id not in self.leads:
            return []
        return sorted(
            self.leads[lead_id]["events"],
            key=lambda x: x["timestamp"]
        )
    
    def get_lead_metrics(self, lead_id: str) -> Dict[str, Any]:
        """Get metrics for a lead."""
        if lead_id not in self.leads:
            return self._init_metrics()
        return self.leads[lead_id]["metrics"]
    
    def get_lead_timeline(self, lead_id: str) -> Dict[str, Any]:
        """Get timeline information for a lead."""
        if lead_id not in self.leads:
            return {
                "first_contact": None,
                "last_email_sent": None,
                "next_scheduled_followup": None
            }
        
        events = self.leads[lead_id]["events"]
        timeline = {
            "first_contact": None,
            "last_email_sent": None,
            "next_scheduled_followup": None
        }
        
        for event in events:
            event_type = event["event_type"]
            timestamp = event["timestamp"]
            
            # Track first contact
            if not timeline["first_contact"]:
                timeline["first_contact"] = timestamp
            
            # Track last email
            if event_type == "email_sent":
                timeline["last_email_sent"] = timestamp
            
            # Track next followup
            if event_type == "followup_scheduled":
                scheduled_time = event["data"].get("scheduled_time")
                if scheduled_time:
                    if not timeline["next_scheduled_followup"] or scheduled_time > timeline["next_scheduled_followup"]:
                        timeline["next_scheduled_followup"] = scheduled_time
        
        return timeline
    
    def _validate_event(self, event: Dict) -> bool:
        """Validate event format."""
        required_fields = ["lead_id", "event_type", "source_agent", "data"]
        return all(field in event for field in required_fields)
    
    def _init_metrics(self) -> Dict[str, Any]:
        """Initialize metrics structure."""
        return {
            "total_events": 0,
            "event_counts": {},
            "email_metrics": {
                "total_sent": 0,
                "total_replies": 0,
                "response_rate": 0.0
            }
        }
    
    def _update_metrics(self, lead_id: str, event: Dict):
        """Update metrics based on new event."""
        metrics = self.leads[lead_id]["metrics"]
        
        # Update total events
        metrics["total_events"] += 1
        
        # Update event counts
        event_type = event["event_type"]
        metrics["event_counts"][event_type] = metrics["event_counts"].get(event_type, 0) + 1
        
        # Update email metrics
        if event_type == "email_sent":
            metrics["email_metrics"]["total_sent"] += 1
            if event["data"]["engagement"]["replied"]:
                metrics["email_metrics"]["total_replies"] += 1
            
            # Update response rate
            total_sent = metrics["email_metrics"]["total_sent"]
            total_replies = metrics["email_metrics"]["total_replies"]
            metrics["email_metrics"]["response_rate"] = (total_replies / total_sent) if total_sent > 0 else 0.0
