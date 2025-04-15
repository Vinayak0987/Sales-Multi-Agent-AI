"""Follow-up Timing Nodes

LangGraph workflow for follow-up timing optimization.
"""

import json
import pandas as pd
from typing import Dict, Any
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END

def create_followup_timing_graph(llm, prompt_templates):
    """Create follow-up timing workflow"""
    workflow = StateGraph(Dict)
    
    # Add nodes (same pattern as other agents)
    workflow.add_node("prepare_data", prepare_data)
    workflow.add_node("analyze_patterns", analyze_patterns)
    workflow.add_node("generate_strategy", lambda x: generate_strategy(x, llm, prompt_templates))
    
    # Linear flow
    workflow.add_edge("prepare_data", "analyze_patterns")
    workflow.add_edge("analyze_patterns", "generate_strategy")
    workflow.add_edge("generate_strategy", END)
    
    workflow.set_entry_point("prepare_data")
    return workflow.compile()

def prepare_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and prepare email data for analysis."""
    print("\n=== prepare_data Step ===")
    
    # Get inputs with defaults
    email_logs = state.get("email_logs", [])
    lead_id = state.get("lead_id", "")
    
    if not lead_id:
        return {**state, "error": "No lead ID provided"}
    
    # Convert list to DataFrame if needed
    if isinstance(email_logs, list):
        if not email_logs:
            return {**state, "error": "No email logs provided"}
        email_logs = pd.DataFrame(email_logs)
    
    # Clean and validate each email
    clean_emails = []
    for _, row in email_logs.iterrows():
        if not row.get("lead_id") == lead_id:
            continue
            
        clean_email = {
            "lead_id": str(row.get("lead_id", "")),
            "sent_time": pd.to_datetime(row.get("sent_time")),
            "replied_time": pd.to_datetime(row.get("replied_time")) if pd.notnull(row.get("replied_time")) else None,
            "email_type": str(row.get("email_type", "other")),
            "response_status": str(row.get("response_status", "pending"))
        }
        clean_emails.append(clean_email)
    
    # Convert back to DataFrame for analysis
    lead_emails = pd.DataFrame(clean_emails)
    
    # Sort by sent time
    if not lead_emails.empty:
        lead_emails = lead_emails.sort_values("sent_time")
    
    # Calculate metrics
    total_emails = len(lead_emails)
    response_rate = len(lead_emails[lead_emails['response_status'] == 'replied']) / total_emails if total_emails > 0 else 0
    
    print(f"Cleaned {total_emails} emails for lead {lead_id}")
    print(f"Response rate: {response_rate:.1%}")
    
    return {
        **state,
        "lead_emails": lead_emails,
        "total_emails": total_emails,
        "response_rate": response_rate,
        "status": "data_prepared"
    }

def analyze_patterns(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze email patterns and calculate timing metrics."""
    print("\n=== analyze_patterns Step ===")
    
    # Get inputs
    lead_emails = state.get("lead_emails")
    total_emails = state.get("total_emails", 0)
    response_rate = state.get("response_rate", 0)
    
    if lead_emails is None:
        return {**state, "error": "Missing lead emails"}
        
    # Validate DataFrame
    if not isinstance(lead_emails, pd.DataFrame):
        return {**state, "error": "Lead emails must be a DataFrame"}
    
    # Calculate timing patterns
    if len(lead_emails) == 0:
        print("No emails found, using default patterns")
        timing_patterns = {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_hours": [10, 14],
            "avg_response_delay": 24
        }
    else:
        try:
            # Get best days/hours from actual data
            sent_times = lead_emails['sent_time']
            best_days = sent_times.dt.day_name().mode().tolist()
            best_hours = sent_times.dt.hour.mode().tolist()
            
            # Use defaults if no patterns found
            if not best_days:
                best_days = ["Tuesday", "Wednesday", "Thursday"]
            if not best_hours:
                best_hours = [10, 14]
            
            # Calculate response delay
            avg_delay = 24  # Default
            if 'replied_time' in lead_emails.columns:
                responded = lead_emails[
                    (lead_emails['response_status'] == 'replied') & 
                    (lead_emails['replied_time'].notna())
                ]
                if len(responded) > 0:
                    replied_times = responded['replied_time']
                    sent_times = responded['sent_time']
                    delays = (replied_times - sent_times).dt.total_seconds() / 3600
                    avg_delay = delays.mean()
                    
            timing_patterns = {
                "best_days": best_days,
                "best_hours": best_hours,
                "avg_response_delay": avg_delay
            }
            
        except Exception as e:
            print(f"Error analyzing patterns: {str(e)}")
            return {**state, "error": f"Failed to analyze patterns: {str(e)}"}
    
    # Calculate urgency (0-100)
    try:
        if total_emails == 0:
            urgency_score = 70  # Default for new leads
        else:
            urgency_score = min(100, max(0,
                50 +  # base
                (total_emails * -10) +  # decrease with more attempts
                (response_rate * 20)  # increase if they respond
            ))
    except Exception as e:
        print(f"Error calculating urgency: {str(e)}")
        urgency_score = 50  # Safe default
    
    print(f"Urgency score: {urgency_score}")
    print(f"Best days: {timing_patterns['best_days']}")
    print(f"Best hours: {timing_patterns['best_hours']}")
    print(f"Avg response delay: {timing_patterns['avg_response_delay']:.1f} hours")
    
    return {
        **state,
        "timing_patterns": timing_patterns,
        "urgency_score": urgency_score,
        "status": "patterns_analyzed"
    }

def generate_strategy(state: Dict[str, Any], llm=None, prompt_templates=None) -> Dict[str, Any]:
    """Generate follow-up strategy using LLM."""
    print("\n=== generate_strategy Step ===")
    
    if not llm or not prompt_templates:
        return {**state, "error": "Missing LLM or prompts"}
        
    # Get context
    context = {
        "total_emails": state.get("total_emails"),
        "response_rate": state.get("response_rate"),
        "timing_patterns": state.get("timing_patterns"),
        "urgency_score": state.get("urgency_score")
    }
    
    print(f"Input context to LLM: {json.dumps(context, indent=2)}")
    
    # Validate context
    if not all(context.values()):
        return {**state, "error": "Missing required context"}
    
    try:
        # Generate strategy using template
        prompt = prompt_templates["generate_strategy"].format(
            context=json.dumps(context, indent=2)
        )
        
        # Get response
        response = llm.generate_content(prompt)
        response_text = response if isinstance(response, str) else response.text
        
        # Parse response
        try:
            # Clean response
            response_text = response_text.strip()
            
            # If response is wrapped in code blocks, extract content
            if response_text.startswith('```') and '```' in response_text[3:]:
                response_text = response_text.split('```', 2)[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
            
            # Find JSON object in the text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            
            # Parse JSON
            strategy = json.loads(response_text)
            
            # Validate strategy
            timing = strategy.get("timing", {})
            follow_up = strategy.get("approach", {})
            
            # Check date is in 2025
            send_date = timing.get("recommended_date", "")
            if not send_date.startswith("2025"):
                print("Warning: Date should be in 2025")
                
            # Check urgency matches follow-up type
            urgency = follow_up.get("urgency", 0)
            follow_type = follow_up.get("type", "")
            
            if urgency <= 30 and follow_type != "soft_nudge":
                print(f"Warning: Urgency {urgency} should use soft_nudge")
            elif 30 < urgency <= 70 and follow_type != "value_add":
                print(f"Warning: Urgency {urgency} should use value_add")
            elif urgency > 70 and follow_type != "social_proof":
                print(f"Warning: Urgency {urgency} should use social_proof")
                
            # Check urgency roughly matches our score
            our_urgency = context["urgency_score"]
            if abs(urgency - our_urgency) > 20:
                print(f"Warning: LLM urgency ({urgency}) differs from ours ({our_urgency})")
            
            print(f"Generated strategy: {json.dumps(strategy, indent=2)}")
            
            return {
                **state,
                "strategy": strategy,
                "status": "completed"
            }
            
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            print(f"Response was: {response_text}")
            return {**state, "error": f"Failed to parse JSON: {str(e)}"}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {**state, "error": str(e)}