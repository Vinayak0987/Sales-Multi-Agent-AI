"""Test Follow-up Timing Agent."""

import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from langgraph_nodes.followup_timing_node import (
    prepare_data,
    analyze_patterns,
    generate_strategy
)
from agents.followup_timing_agent import FollowUpTimingAgent

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_data_processing():
    """Test data processing without LLM"""
    print("\n=== Testing Data Processing ===")
    
    # Create test data
    test_data = pd.DataFrame({
        'email_id': ['E001', 'E002', 'E003'],
        'lead_id': ['L001', 'L001', 'L001'],
        'sent_time': pd.to_datetime([
            '2024-04-01 10:00:00',
            '2024-04-03 14:00:00',
            '2024-04-05 11:00:00'
        ]),
        'replied_time': pd.to_datetime([
            '2024-04-01 11:00:00',
            None,
            None
        ]),
        'email_type': ['initial', 'followup_1', 'followup_2'],
        'response_status': ['replied', 'ignored', 'ignored']
    })
    
    # Test prepare_data
    print("\nTesting prepare_data...")
    initial_state = {
        "lead_id": "L001",
        "email_logs": test_data
    }
    
    try:
        prepared = prepare_data(initial_state)
        assert "lead_emails" in prepared
        assert "total_emails" in prepared
        assert "response_rate" in prepared
        assert prepared["total_emails"] == 3
        assert prepared["response_rate"] == 1/3
        print("✓ prepare_data passed")
    except Exception as e:
        print(f"✗ prepare_data failed: {str(e)}")
        raise
    
    # Test analyze_patterns
    print("\nTesting analyze_patterns...")
    try:
        analyzed = analyze_patterns(prepared)
        assert "timing_patterns" in analyzed
        assert "urgency_score" in analyzed
        patterns = analyzed["timing_patterns"]
        assert "best_days" in patterns
        assert "best_hours" in patterns
        assert 0 <= analyzed["urgency_score"] <= 100
        print("✓ analyze_patterns passed")
    except Exception as e:
        print(f"✗ analyze_patterns failed: {str(e)}")
        raise

def main():
    """Run all tests"""
    test_data_processing()
    
    # Setup LLM
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")
    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel('gemini-2.5-flash')
    
    # Test full agent
    print("\nFollow-up Timing Agent created")
    agent = FollowUpTimingAgent(llm)  # Pass LLM
    
    # Load test data
    test_data = pd.DataFrame({
        'email_id': ['E001', 'E002', 'E003'],
        'lead_id': ['L001', 'L001', 'L001'],
        'sent_time': pd.to_datetime([
            '2024-04-01 09:00:00',
            '2024-04-05 14:00:00',
            '2024-04-10 10:00:00'
        ]),
        'replied_time': pd.to_datetime([
            '2024-04-01 10:00:00',
            None,
            None
        ]),
        'email_type': ['initial', 'followup_1', 'followup_2'],
        'response_status': ['replied', 'ignored', 'ignored']
    })
    
    agent.load_data(test_data)
    print("\nLoaded email logs")
    
    # For README: Show input data
    print("\n=== Followup Timing Input ===")
    input_data = {
        "lead_id": "L001",
        "email_history": [
            {
                "type": test_data.iloc[0]["email_type"],
                "sent": str(test_data.iloc[0]["sent_time"]),
                "response": test_data.iloc[0]["response_status"]
            },
            {
                "type": test_data.iloc[1]["email_type"],
                "sent": str(test_data.iloc[1]["sent_time"]),
                "response": test_data.iloc[1]["response_status"]
            }
        ]
    }
    print(json.dumps(input_data, indent=2))
    
    # Test cases - KEEPING ORIGINAL
    print("\n=== Test Case 1: First Follow-up ===")
    result = agent.process_task("L001")  # Lead with just initial email
    assert "timing" in result
    assert "approach" in result  
    assert "engagement_prediction" in result
    
    # For README: Show key output
    print("\n=== Followup Timing Output ===")
    output = {
        "timing": result["timing"],
        "approach": result["approach"],
        "engagement_prediction": result["engagement_prediction"]
    }
    print(json.dumps(output, indent=2))
    
    # Save output to file
    output_file = os.path.join(OUTPUT_DIR, "followup_timing_output.json")
    output_data = {
        "agent": "Follow-Up Timing Agent",
        "timestamp": datetime.now().isoformat(),
        "input": input_data,
        "result": result,
        "summary": output
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\n✅ Output saved to: {output_file}")

if __name__ == "__main__":
    main()
