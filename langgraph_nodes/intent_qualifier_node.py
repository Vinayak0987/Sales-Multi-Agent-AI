"""Intent Qualifier Node

This module contains the nodes for the Intent Qualifier Agent's LangGraph workflow.
Focuses on identifying high-intent leads based on behavior patterns.
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph
import json
import pandas as pd

def prepare_data(state):
    """Clean and prepare lead data - no LLM needed"""
    print("\n=== prepare_data Step ===")
    
    # Get raw data
    leads = state.get("lead_data", [])
    emails = state.get("email_data", [])
    
    # Clean leads - remove empty/invalid records
    clean_leads = []
    for lead in leads:
        if not lead or not lead.get("lead_id"):
            continue
        clean_lead = {
            "lead_id": str(lead.get("lead_id", "")),
            "company": str(lead.get("company", "")),
            "title": str(lead.get("title", "")),
            "industry": str(lead.get("industry", "Unknown")),
            "visits": int(lead.get("visits", 0)),
            "time_on_site": float(lead.get("time_on_site", 0.0)),
            "pages_per_visit": float(lead.get("pages_per_visit", 0.0)),
            "converted": bool(lead.get("converted", False))
        }
        clean_leads.append(clean_lead)
    
    # Clean emails - remove empty/invalid records
    clean_emails = []
    for email in emails:
        if not email or not email.get("lead_id"):
            continue
        clean_email = {
            "email_id": str(email.get("email_id", "")),
            "lead_id": str(email.get("lead_id", "")),
            "opened": bool(email.get("opened", False)),
            "replied": bool(email.get("reply_status") == "replied"),
            "engagement_score": float(email.get("engagement_score", 0.0))
        }
        clean_emails.append(clean_email)
    
    print(f"Cleaned {len(clean_leads)} leads and {len(clean_emails)} emails")
    print("\nSample clean lead:", json.dumps(clean_leads[0], indent=2) if clean_leads else "No leads")
    print("\nSample clean email:", json.dumps(clean_emails[0], indent=2) if clean_emails else "No emails")
    
    return {
        **state,
        "lead_data": clean_leads,
        "email_data": clean_emails,
        "status": "data_prepared"
    }

def analyze_patterns(state):
    """Analyze patterns using basic stats - no LLM needed"""
    print("\n=== analyze_patterns Step ===")
    
    leads = state.get("lead_data", [])
    emails = state.get("email_data", [])
    
    print(f"Analyzing {len(leads)} leads and {len(emails)} emails")
    
    # Calculate intent scores for each lead
    scored_leads = []
    for lead in leads:
        lead_id = lead["lead_id"]
        
        # Get emails for this lead
        lead_emails = [e for e in emails if e["lead_id"] == lead_id]
        
        # Calculate engagement metrics
        email_score = sum([
            e["engagement_score"] * 2 +  # Base engagement
            (2 if e["replied"] else 1 if e["opened"] else 0)  # Additional points for actions
            for e in lead_emails
        ])
        
        # Calculate intent score (0-100)
        intent_score = min(100, sum([
            email_score * 10,  # Email engagement (0-50)
            min(50, lead["visits"] * 5),  # Website activity (0-50)
            min(50, lead["pages_per_visit"] * 10),  # Content interest (0-50)
            (30 if lead["converted"] else 0)  # Conversion bonus
        ]) / 2)  # Normalize to 0-100
        
        # Determine qualification signals
        signals = [
            # Email engagement signals
            "high_email_engagement" if email_score > 5 else None,
            "responsive_to_emails" if any(e["replied"] for e in lead_emails) else None,
            
            # Website behavior signals
            "active_website_visitor" if lead["visits"] > 3 else None,
            "deep_content_researcher" if lead["pages_per_visit"] > 3 else None,
            "long_session_visitor" if lead["time_on_site"] > 300 else None,  # 5+ minutes
            
            # Conversion signals
            "converted_lead" if lead["converted"] else None
        ]
        
        scored_leads.append({
            **lead,
            "intent_score": intent_score,
            "email_engagement": email_score,
            "qualification_signals": [s for s in signals if s]
        })
    
    # Sort by intent score
    scored_leads.sort(key=lambda x: x["intent_score"], reverse=True)
    
    # Segment leads by intent score
    segments = {
        "high_intent": [l for l in scored_leads if l["intent_score"] >= 50],
        "medium_intent": [l for l in scored_leads if 30 <= l["intent_score"] < 50],
        "low_intent": [l for l in scored_leads if l["intent_score"] < 30]
    }
    
    print(f"\nSegmented {len(scored_leads)} leads:")
    print(f"- High Intent: {len(segments['high_intent'])}")
    print(f"- Medium Intent: {len(segments['medium_intent'])}")
    print(f"- Low Intent: {len(segments['low_intent'])}")
    
    if scored_leads:
        print("\nTop lead:")
        top_lead = scored_leads[0]
        print(f"- Score: {top_lead['intent_score']:.1f}")
        print(f"- Signals: {top_lead['qualification_signals']}")
    
    return {
        **state,
        "scored_leads": scored_leads,
        "intent_segments": segments,
        "status": "patterns_analyzed"
    }

def generate_insights(state, llm=None, prompt_templates=None):
    """Generate insights using LLM"""
    print("\n=== generate_insights Step ===")
    
    if not llm or not prompt_templates:
        return {**state, "status": "error", "error": "Missing LLM or prompts"}
    
    # Prepare data for LLM
    high_intent = state["intent_segments"]["high_intent"]
    medium_intent = state["intent_segments"]["medium_intent"]
    
    # Get statistics
    analysis_data = {
        "total_leads": len(state["scored_leads"]),
        "high_intent_count": len(high_intent),
        "medium_intent_count": len(medium_intent),
        "avg_intent_score": sum(l["intent_score"] for l in state["scored_leads"]) / len(state["scored_leads"]),
        "top_signals": [
            signal for lead in high_intent + medium_intent[:10]
            for signal in lead["qualification_signals"]
            if signal
        ][:5]
    }
    
    # Get sample emails
    sample_emails = []
    for lead in high_intent[:3]:
        lead_emails = [e for e in state["email_data"] if e["lead_id"] == lead["lead_id"]]
        if lead_emails:
            sample_emails.extend(lead_emails[:2])
    
    # Get insights from LLM
    prompt = prompt_templates["generate_insights"].format(
        lead_data=json.dumps(analysis_data, indent=2),
        email_data=json.dumps(sample_emails[:5], indent=2)
    )
    
    try:
        print("Generating insights from LLM...")
        response = llm.generate_content(prompt)
        print("\nRaw LLM response:", response)
        
        # Clean the response - remove any non-JSON text
        json_str = response if isinstance(response, str) else response.text
        json_start = json_str.find("{")
        json_end = json_str.rfind("}") + 1
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = json_str[json_start:json_end]
        insights = json.loads(json_str)
        
        # Validate response structure
        if not isinstance(insights.get("intent_signals"), list):
            raise ValueError("Missing or invalid intent_signals array")
        if not isinstance(insights.get("recommendations"), list):
            raise ValueError("Missing or invalid recommendations array")
        
        print("\nSuccessfully parsed insights:")
        print(f"- {len(insights['intent_signals'])} intent signals")
        print(f"- {len(insights['recommendations'])} recommendations")
        
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        insights = {
            "intent_signals": [
                {
                    "signal": "Error processing insights",
                    "strength": "low",
                    "evidence": str(e)
                }
            ],
            "recommendations": [
                {
                    "action": "Review error and retry",
                    "priority": "high",
                    "reasoning": "Failed to generate insights"
                }
            ]
        }
    
    return {
        **state,
        "insights": insights,
        "qualified_leads": high_intent,
        "status": "completed"
    }

def create_intent_qualifier_graph(llm, prompt_templates):
    """Create the LangGraph workflow for intent qualification"""
    print("\n=== Creating Intent Qualifier Graph ===")
    
    # Create workflow
    workflow = StateGraph(state_schema=Dict[str, Any])
    
    # Add nodes
    workflow.add_node("prepare_data", prepare_data)
    workflow.add_node("analyze_patterns", analyze_patterns)
    workflow.add_node("generate_insights", lambda state: generate_insights(state, llm, prompt_templates))
    
    # Define edges
    workflow.add_edge("prepare_data", "analyze_patterns")
    workflow.add_edge("analyze_patterns", "generate_insights")
    
    # Set entry and end points
    workflow.set_entry_point("prepare_data")
    workflow.set_finish_point("generate_insights")
    
    return workflow.compile()