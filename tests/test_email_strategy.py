"""Test Email Strategy Agent"""

import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from agents.email_strategy_agent import EmailStrategyAgent

def test_email_strategy():
    """Test email strategy agent with a single qualified lead"""
    
    # Wait to avoid rate limits
    print("\nWaiting 60 seconds to avoid rate limits...")
    time.sleep(60)
    
    # Setup LLM - KEEPING ORIGINAL SETUP
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")
    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel('models/gemini-1.5-pro')
    print(f"Using model: {llm.model_name}")
    
    # Setup company info
    company_info = {
        "name": "Codeium",
        "sender_name": "Alex Chen",
        "sender_title": "AI Solutions Architect",
        "value_prop": "helping engineering teams boost productivity with AI-powered development tools"
    }
    
    # Create email agent
    email_agent = EmailStrategyAgent(llm, company_info)
    print("\nEmail Strategy Agent created")
    
    # Load successful email examples
    email_agent.load_data("data/Email_Logs.csv")
    
    # Create a qualified lead
    qualified_lead = {
        "lead_id": "L245",
        "company": "DataFlow Inc",
        "title": "Engineering Manager",
        "industry": "Data Analytics",
        "visits": 15,
        "time_on_site": 450,  # 7.5 minutes
        "pages_per_visit": 4.0,
        "converted": False,  # Haven't requested trial yet
        "intent_score": 70.0  # Medium-high intent score
    }
    
    # Create intent data
    intent_insights = {
        "intent_signals": [
            {
                "signal": "Content Engagement",
                "strength": "medium",
                "evidence": "Downloaded 2 whitepapers on code automation"
            },
            {
                "signal": "Team Pain Points",
                "strength": "high",
                "evidence": "Searched for 'code review automation' and 'team productivity'"
            },
            {
                "signal": "Budget Research",
                "strength": "medium",
                "evidence": "Multiple visits to pricing page, no trial request yet"
            }
        ],
        "recommendations": [
            {
                "action": "Share ROI Calculator",
                "priority": "high",
                "reasoning": "Shows interest in value/cost analysis through pricing page visits"
            },
            {
                "action": "Highlight Team Features",
                "priority": "high",
                "reasoning": "Search history indicates team-wide solution interest"
            }
        ]
    }
    
    # For README: Show input data
    print("\n=== Email Strategy Input ===")
    input_data = {
        "lead": {
            "company": str(qualified_lead["company"]),
            "title": str(qualified_lead["title"]),
            "industry": str(qualified_lead["industry"]),
            "intent_score": float(qualified_lead["intent_score"])
        },
        "intent_signals": intent_insights["intent_signals"][:2],  # Show top 2 signals
        "company_info": {
            "name": str(company_info["name"]),
            "sender_title": str(company_info["sender_title"])
        }
    }
    print(json.dumps(input_data, indent=2))
    
    # Craft personalized email
    email = email_agent.craft_email(
        lead=qualified_lead,
        intent_data=intent_insights
    )
    
    # For README: Show key output
    print("\n=== Email Strategy Output ===")
    output = {
        "subject": str(email["subject"]),
        "personalization_factors": email["personalization"][:2],  # Show top 2 factors
        "email_preview": str(email["body"][:150]) + "..."  # Show first 150 chars
    }
    print(json.dumps(output, indent=2))
    
    # Print result
    print("\n=== Final Email ===")
    print(f"To: {qualified_lead['title']} @ {qualified_lead['company']}")
    print(f"Subject: {email['subject']}\n")
    print(email['body'])
    print(f"\nPersonalization Factors:")
    for factor in email['personalization']:
        print(f"- {factor}")

    return {
        "agent": email_agent,
        "lead": qualified_lead,
        "intent_data": intent_insights,
        "email": email,
        "llm": llm
    }

if __name__ == "__main__":
    test_result = test_email_strategy()
