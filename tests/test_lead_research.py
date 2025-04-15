import os
import json
import time
import pandas as pd
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai
from agents.lead_research_agent import LeadResearchAgent

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
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    print("LLM setup complete")
    return model

def test_lead_research_agent():
    """Test the LeadResearch agent with real data"""
    
    # Wait to avoid rate limits
    print("\nWaiting 60 seconds to avoid rate limits...")
    time.sleep(60)
    
    # Setup LLM
    llm = setup_llm()
    print(f"Using model: {llm.model_name}")
    
    # Create agent with fresh LLM
    agent = LeadResearchAgent(llm)
    print("\nAgent created")
    
    # Load real data
    leads_df = pd.read_csv('data/Leads_Data.csv')
    sales_df = pd.read_csv('data/Sales_Pipeline.csv')
    
    # Take one real test case
    test_lead = leads_df.iloc[0]
    test_sale = sales_df[sales_df['lead_id'] == test_lead['lead_id']].iloc[0] if len(sales_df[sales_df['lead_id'] == test_lead['lead_id']]) > 0 else None
    
    # For README: Show input data
    print("\n=== Lead Research Input ===")
    input_data = {
        "lead": {
            "company": str(test_lead['company']),
            "region": str(test_lead['region']),
            "source": str(test_lead['lead_source']),
            "visits": int(test_lead['visits']),
            "time_on_site": float(test_lead['time_on_site']),
            "pages_per_visit": float(test_lead['pages_per_visit'])
        }
    }
    print(json.dumps(input_data, indent=2))
    
    # Save to temporary files for the agent
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as leads_file:
        pd.DataFrame([test_lead]).to_csv(leads_file.name, index=False)
        leads_path = leads_file.name
        
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as sales_file:
        if test_sale is not None:
            pd.DataFrame([test_sale]).to_csv(sales_file.name, index=False)
        else:
            pd.DataFrame(columns=sales_df.columns).to_csv(sales_file.name, index=False)
        sales_path = sales_file.name
    
    # Load data into agent
    agent.load_data(leads_path, sales_path)
    
    # Create a test task
    task = {
        "input": "Analyze the lead data and provide insights",
        "id": "task_1",
        "type": "lead_research"
    }
    
    # Process task
    result = agent.process_task(task)
    result_json = json.loads(result)
    
    # For README: Show key output
    print("\n=== Lead Research Output ===")
    output = {
        "quality_indicators": result_json["lead_quality_indicators"]["behavioral"][:2],  # Show top 2 indicators
        "recommendation": result_json["engagement_recommendations"][0]  # Show top recommendation
    }
    print(json.dumps(output, indent=2))
    
    # Cleanup
    os.unlink(leads_path)
    os.unlink(sales_path)
    
    return {
        "agent": agent,
        "test_lead": test_lead,
        "test_sale": test_sale,
        "result": result_json,
        "llm": llm
    }

if __name__ == "__main__":
    test_lead_research_agent()