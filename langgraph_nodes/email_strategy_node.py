"""Email Strategy Nodes

LangGraph workflow for email crafting.
"""

import json
import pandas as pd
from typing import Dict, Any
from langgraph.graph import StateGraph, END

def create_email_strategy_graph(llm, prompt_templates):
    """Create email strategy workflow"""
    workflow = StateGraph(Dict)
    
    # Add nodes (same pattern as Lead Research)
    workflow.add_node("prepare_data", prepare_data)
    workflow.add_node("analyze_patterns", analyze_patterns)
    workflow.add_node("generate_email", lambda x: generate_email(x, llm, prompt_templates))
    
    # Linear flow
    workflow.add_edge("prepare_data", "analyze_patterns")
    workflow.add_edge("analyze_patterns", "generate_email")
    workflow.add_edge("generate_email", END)
    
    workflow.set_entry_point("prepare_data")
    return workflow.compile()

def prepare_data(state):
    """Clean and validate data - no LLM needed"""
    print("\n=== prepare_data Step ===")
    
    # Check intent qualification
    lead = state.get("lead_data", {})
    if not lead:
        return {**state, "error": "No lead data provided"}
    
    intent_score = lead.get("intent_score", 0) / 100  # Convert to 0-1 scale
    if intent_score < 0.6:  # Only proceed with qualified leads
        return {**state, "error": f"Lead not qualified (intent score: {intent_score})"}
    
    # Get inputs
    emails = state.get("email_data", [])
    if not emails:
        return {**state, "error": "No historical emails provided"}
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(emails)
    
    # Convert to bool
    df['opened'] = df['opened'].astype(bool)
    df['reply_status'] = df['reply_status'].astype(bool)
    
    # Keep only successful emails
    successful = df[df['opened'] & df['reply_status']]
    clean_emails = successful.to_dict('records')
    
    return {
        **state,
        "clean_emails": clean_emails,
        "status": "data_prepared"
    }

def analyze_patterns(state):
    """Find similar examples - no LLM needed"""
    print("\n=== analyze_patterns Step ===")
    
    lead = state.get("lead_data", {})
    emails = state.get("clean_emails", [])
    intent_data = state.get("intent_data", {})
    
    if not lead or not emails:
        return {**state, "error": "Missing clean data"}
    
    # Find similar examples by industry
    similar = []
    for email in emails:
        if email.get('industry') == lead.get('industry'):
            similar.append(email)
    
    # Use best examples
    examples = similar[:5] if similar else emails[:5]
    
    # Format context with defaults
    context = {
        "lead": {
            "company": lead.get('company', ''),
            "industry": lead.get('industry', ''),
            "title": lead.get('title', '')
        },
        "company": state.get("company_info", {}),
        "intent": {
            "score": intent_data.get("intent_score", 0),
            "signals": intent_data.get("intent_signals", []),
            "recommendations": intent_data.get("recommendations", [])
        },
        "examples": [{
            "subject": ex.get('subject', 'Product Demo Request'),
            "email_text": ex.get('email_text', ''),
            "industry": ex.get('industry', 'Technology'),
            "sentiment": ex.get('sentiment', 'positive'),
            "engagement_score": ex.get('engagement_score', 0.8)
        } for ex in examples],
        "total_examples": len(examples)
    }
    
    return {
        **state,
        "email_context": context,
        "status": "patterns_analyzed"
    }

def generate_email(state, llm=None, prompt_templates=None):
    """Generate email using LLM"""
    print("\n=== generate_email Step ===")
    
    if not llm or not prompt_templates:
        return {**state, "error": "Missing LLM or prompts"}
    
    context = state.get("email_context")
    if not context:
        return {**state, "error": "Missing email context"}
    
    try:
        # Generate email using template
        prompt = prompt_templates["craft_email"].format(
            context=json.dumps(context, indent=2)
        )
        
        # Get response
        response = llm.generate_content(prompt)
        response_text = response if isinstance(response, str) else response.text
        
        # Parse response
        try:
            # Clean response
            response_text = response_text.strip()
            if response_text.startswith('```'):
                response_text = response_text[response_text.find('{'):response_text.rfind('}')+1]
            
            # Parse JSON
            email = json.loads(response_text)
            
            # Validate
            required = ["subject", "body", "personalization"]
            for field in required:
                if not email.get(field):
                    raise ValueError(f"Missing {field} in email")
            
            return {
                **state,
                "crafted_email": email,
                "status": "completed"
            }
            
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            print(f"Response was: {response_text}")
            raise ValueError("Failed to parse email")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {**state, "error": str(e)}
