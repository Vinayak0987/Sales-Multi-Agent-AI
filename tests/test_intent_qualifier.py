"""Test Intent Qualifier Agent

This module tests the Intent Qualifier Agent with real data.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from agents.intent_qualifier_agent import IntentQualifierAgent
import time

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load environment variables
load_dotenv()

def setup_llm():
    """Setup Google AI LLM for testing"""
    print("\nSetting up Google AI LLM...")
    
    # Configure Google AI with API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    genai.configure(api_key=api_key)
    
    # Create model
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("LLM setup complete")
    
    # Create wrapper
    class GeminiWrapper:
        def __init__(self, model):
            self.model = model
            self.model_name = model.model_name
        
        def generate_content(self, prompt):
            response = self.model.generate_content(prompt)
            return str(response.text) if hasattr(response, 'text') else str(response)
    
    return GeminiWrapper(model)

def test_intent_qualifier():
    """Test the Intent Qualifier Agent with real data"""
    
    # Setup LLM
    llm = setup_llm()
    print(f"Using model: {llm.model_name}")
    
    # Create agent
    agent = IntentQualifierAgent(llm)
    print("\nAgent created")
    
    # Load real data
    leads_path = "data/Leads_Data.csv"
    email_path = "data/Email_Logs.csv"
    agent.load_data(leads_path, email_path)
    
    # Use real lead with strong signals
    lead = {
        "lead_id": "L003",
        "company": "CloudTech",
        "title": "VP Engineering",
        "industry": "Cloud Services",
        "visits": 30,
        "time_on_site": 900,  # 15 minutes
        "pages_per_visit": 6.0,
        "converted": True  # They requested a trial
    }
    
    # Real conversation showing strong buying signals
    conversation = [
        "Our cloud infrastructure team needs better code review tools",
        "We have 100+ microservices and reviews are a bottleneck",
        "AI-powered automation looks promising for our scale",
        "Budget is approved, looking for proven solutions",
        "Need to move fast - can we start a trial next week?"
    ]
    
    # For README: Show input data
    print("\n=== Intent Qualifier Input ===")
    input_data = {
        "lead": {
            "company": str(lead["company"]),
            "title": str(lead["title"]),
            "industry": str(lead["industry"]),
            "visits": int(lead["visits"]),
            "time_on_site": float(lead["time_on_site"]),
            "pages_per_visit": float(lead["pages_per_visit"])
        },
        "conversation_sample": conversation[:2]  # Show first 2 messages
    }
    print(json.dumps(input_data, indent=2))
    
    # Process qualification task
    result = agent.process_task({
        "lead": lead,
        "conversation": conversation
    })
    
    # For README: Show key output
    print("\n=== Intent Qualifier Output ===")
    output = {
        "intent_score": float(result["qualified_leads"][0]["intent_score"]),
        "key_signals": result["insights"]["intent_signals"][:2],  # Show top 2 signals
        "recommendation": result["insights"]["recommendations"][0]  # Show top recommendation
    }
    print(json.dumps(output, indent=2))
    
    # Save output to file
    output_file = os.path.join(OUTPUT_DIR, "intent_qualifier_output.json")
    output_data = {
        "agent": "Intent Qualifier Agent",
        "timestamp": datetime.now().isoformat(),
        "input": input_data,
        "result": result,
        "summary": output
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\n✅ Output saved to: {output_file}")
    
    return {
        "agent": agent,
        "lead": lead,
        "conversation": conversation,
        "result": result,
        "llm": llm
    }

if __name__ == "__main__":
    test_result = test_intent_qualifier()