import os
import pandas as pd
from datetime import datetime, timedelta
from agents.crm_logger_agent import CRMLoggerAgent
import json

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_with_real_data():
    """Test CRM Logger with real data from all agents."""
    
    # Initialize CRM Logger
    crm_logger = CRMLoggerAgent()
    
    # Load all data
    leads_data = pd.read_csv("data/Leads_Data.csv")
    email_logs = pd.read_csv("data/Email_Logs.csv")
    crm_pipeline = pd.read_csv("data/CRM_Pipeline.csv")
    sales_pipeline = pd.read_csv("data/Sales_Pipeline.csv")
    
    print("\n=== Testing with real data ===")
    print(f"Loaded {len(leads_data)} leads")
    print(f"Loaded {len(email_logs)} emails")
    print(f"Loaded {len(crm_pipeline)} pipeline events")
    print(f"Loaded {len(sales_pipeline)} sales events")
    
    # Get test lead with email interactions
    test_leads = leads_data[leads_data["lead_id"].isin(email_logs["lead_id"].unique())]
    if len(test_leads) == 0:
        print("No leads found with email interactions")
        return
    
    test_lead = test_leads.iloc[0]
    lead_id = str(test_lead["lead_id"])
    print(f"\nTesting with lead_id: {lead_id}")
    
    # For README: Show sample input
    print("\n=== CRM Logger Input ===")
    sample_event = {
        "lead_id": lead_id,
        "source_agent": "email_strategy",
        "event_type": "email_sent",
        "email_id": "E123",
        "subject": "Follow-up on our conversation",
        "engagement_score": 0.85
    }
    print(json.dumps(sample_event, indent=2))
    
    # 1. Lead Research Event
    lead_research_event = {
        "lead_id": lead_id,
        "source_agent": "lead_research",
        "company": test_lead["company"],
        "region": test_lead["region"],
        "visits": test_lead["visits"],
        "time_on_site": test_lead["time_on_site"],
        "pages_per_visit": test_lead["pages_per_visit"]
    }
    result = crm_logger.process_event(lead_research_event)
    assert result["status"] == "success", f"Failed to process lead research event: {result}"
    
    # 2. Intent Qualifier & Email Events
    lead_emails = email_logs[email_logs["lead_id"] == lead_id]
    for _, email in lead_emails.iterrows():
        # Intent Event
        intent_event = {
            "lead_id": lead_id,
            "source_agent": "intent_qualifier",
            "intent_score": float(email["engagement_score"]),
            "confidence_tag": email["confidence_tag"],
            "intent_signals": [{
                "signal": "Email Engagement",
                "strength": "high" if float(email["engagement_score"]) > 0.7 else "medium",
                "evidence": f"Engagement score: {email['engagement_score']}"
            }]
        }
        result = crm_logger.process_event(intent_event)
        assert result["status"] == "success", f"Failed to process intent event: {result}"
        
        # Email Event
        email_event = {
            "lead_id": lead_id,
            "source_agent": "email_strategy",
            "email_id": str(email["email_id"]),
            "subject": email["subject"],
            "email_type": email["email_type"],
            "sent_time": datetime.now().isoformat(),
            "opened": bool(email["opened"]),
            "reply_status": email["reply_status"],
            "engagement_score": float(email["engagement_score"])
        }
        result = crm_logger.process_event(email_event)
        assert result["status"] == "success", f"Failed to process email event: {result}"
    
    # 3. Followup Events
    lead_pipeline = crm_pipeline[crm_pipeline["lead_id"] == lead_id]
    for _, pipeline in lead_pipeline.iterrows():
        followup_event = {
            "lead_id": lead_id,
            "source_agent": "followup_timing",
            "scheduled_time": (datetime.now() + timedelta(days=3)).isoformat(),
            "followup_type": "email",
            "urgency_score": 75.0,
            "timing_patterns": {
                "best_days": ["Tuesday", "Wednesday"],
                "best_hours": [10, 14]
            }
        }
        result = crm_logger.process_event(followup_event)
        assert result["status"] == "success", f"Failed to process followup event: {result}"
    
    # Test retrieval functions
    print("\n=== Testing Retrieval Functions ===")
    
    # 1. Get lead history
    history = crm_logger.get_lead_history(lead_id)
    print("\n=== Lead History ===")
    print(f"Total events for lead {lead_id}: {len(history)}")
    print("Event types:", set(e["event_type"] for e in history))
    
    # 2. Get metrics
    metrics = crm_logger.get_lead_metrics(lead_id)
    print("\n=== Lead Metrics ===")
    print("Total events:", metrics["total_events"])
    print("Event counts:", metrics["event_counts"])
    print("Email metrics:", metrics["email_metrics"])
    
    # 3. Get timeline
    timeline = crm_logger.get_lead_timeline(lead_id)
    print("\n=== Lead Timeline ===")
    print("First contact:", timeline["first_contact"])
    print("Last email sent:", timeline["last_email_sent"])
    print("Next followup:", timeline["next_scheduled_followup"])
    
    # For README: Show key insights
    print("\n=== CRM Logger Output ===")
    key_insights = {
        "lead_summary": {
            "total_events": metrics["total_events"],
            "event_types": list(metrics["event_counts"].keys()),
            "response_rate": metrics["email_metrics"]["response_rate"]
        },
        "timeline": {
            "first_contact": timeline["first_contact"],
            "last_contact": timeline["last_email_sent"],
            "next_followup": timeline["next_scheduled_followup"]
        }
    }
    print(json.dumps(key_insights, indent=2))
    
    # Save output to file
    output_file = os.path.join(OUTPUT_DIR, "crm_logger_output.json")
    output_data = {
        "agent": "CRM Logger Agent",
        "timestamp": datetime.now().isoformat(),
        "input": sample_event,
        "metrics": metrics,
        "timeline": timeline,
        "summary": key_insights
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\n✅ Output saved to: {output_file}")

if __name__ == "__main__":
    test_with_real_data()
