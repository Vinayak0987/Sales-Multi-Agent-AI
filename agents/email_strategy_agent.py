"""Email Strategy Agent

This module contains the Email Strategy Agent class for crafting personalized sales emails.
Uses LangGraph for workflow management.
"""

from typing import Dict, List, Any
import pandas as pd
import json
from langgraph_nodes.email_strategy_node import create_email_strategy_graph
from prompts.email_strategy_prompts import email_strategy_prompts

class EmailStrategyAgent:
    def __init__(self, llm, company_info: Dict[str, str]):
        """Initialize the agent with an LLM instance and company info"""
        self.llm = llm
        self.company_info = company_info
        self.email_data = None
    
    def load_data(self, email_path: str):
        """Load historical email data from CSV"""
        print("\n=== Loading Data ===")
        
        # Load emails
        self.email_data = pd.read_csv(email_path)
        print(f"Loaded email data shape: {self.email_data.shape}")
        print(f"Email columns: {self.email_data.columns.tolist()}")
    
    def _validate_data(self):
        """Validate and prepare data for the workflow"""
        if self.email_data is None:
            raise ValueError("Must load data before processing")
        
        # Convert emails to list format
        emails_list = []
        for _, row in self.email_data.iterrows():
            email = {
                "email_id": str(row.get("email_id", "")),
                "subject": str(row.get("subject", "")),
                "email_text": str(row.get("email_text", "")),
                "stage": str(row.get("stage", "")),
                "opened": bool(row.get("opened", False)),
                "reply_status": bool(row.get("replied", False)),
                "sentiment": str(row.get("sentiment", "")),
                "engagement_score": float(row.get("engagement_score", 0))
            }
            emails_list.append(email)
        
        return emails_list
    
    def craft_email(self, lead: Dict[str, Any], intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Craft a personalized email for a qualified lead"""
        print("\n=== Crafting Email ===")
        
        try:
            # Get email examples
            emails = self._validate_data()
            print(f"Found {len(emails)} email examples")
            
            # Get successful examples
            successful = [e for e in emails if e.get('opened') and e.get('reply_status')]  # Fix: check bool
            examples = successful[:5]  # Use top 5
            print(f"Using {len(examples)} successful examples")
            
            # Format context for LLM
            context = {
                "lead": {
                    "company": lead.get('company'),
                    "title": lead.get('title'),
                    "industry": lead.get('industry')
                },
                "company": self.company_info,
                "intent": {
                    "score": lead.get('intent_score', 0),
                    "signals": intent_data.get('intent_signals', []),
                    "recommendations": intent_data.get('recommendations', [])
                },
                "examples": examples
            }
            
            # Generate email using LLM
            prompt = email_strategy_prompts["craft_email"].format(
                context=json.dumps(context, indent=2)
            )
            
            print("\n=== Generating Email ===")
            response = self.llm.generate_content(prompt)
            response_text = response.text
            
            # Clean up markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1]
                response_text = response_text.split("```")[0]
            
            print(f"Cleaned response: {response_text}")
            
            email = json.loads(response_text)
            print("\n=== Parsed Email ===")
            print(json.dumps(email, indent=2))
            
            # Validate required fields
            required = ["subject", "body", "personalization"]
            for field in required:
                if not email.get(field):
                    raise ValueError(f"Missing {field} in email")
                    
            return email
            
        except Exception as e:
            print(f"\n=== Error Details ===")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            raise ValueError(f"Failed to craft email: {str(e)}")
