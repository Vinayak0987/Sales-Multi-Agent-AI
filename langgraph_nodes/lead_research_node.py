from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph
import pandas as pd
import json

def validate_llm_response(response: str) -> dict:
    """Validate and parse LLM response to ensure it matches expected format"""
    try:
        # Try to parse as JSON
        if not isinstance(response, str):
            raise ValueError(f"Response must be a string, got {type(response)}")
        
        data = json.loads(response)
        
        # Validate insights array
        if not isinstance(data.get("insights"), list):
            raise ValueError("insights must be an array")
        
        for insight in data["insights"]:
            # Check required fields
            required = ["pattern", "reasoning", "evidence", "opportunity_score", "learning"]
            missing = [f for f in required if f not in insight]
            if missing:
                raise ValueError(f"Missing required fields in insight: {missing}")
            
            # Validate evidence structure
            evidence = insight["evidence"]
            if not isinstance(evidence, dict):
                raise ValueError("evidence must be an object")
            
            evidence_required = ["conversion_rate", "sample_size", "key_indicators"]
            missing = [f for f in evidence_required if f not in evidence]
            if missing:
                raise ValueError(f"Missing required fields in evidence: {missing}")
            
            # Type checks
            if not isinstance(evidence["conversion_rate"], (int, float)):
                raise ValueError("conversion_rate must be a number")
            if not isinstance(evidence["sample_size"], int):
                raise ValueError("sample_size must be an integer")
            if not isinstance(evidence["key_indicators"], list):
                raise ValueError("key_indicators must be an array")
            if not isinstance(insight["opportunity_score"], (int, float)):
                raise ValueError("opportunity_score must be a number")
            
            # Range checks
            if not 0 <= evidence["conversion_rate"] <= 1:
                raise ValueError("conversion_rate must be between 0 and 1")
            if evidence["sample_size"] <= 0:
                raise ValueError("sample_size must be positive")
            if not 0 <= insight["opportunity_score"] <= 1:
                raise ValueError("opportunity_score must be between 0 and 1")
        
        # Validate discovery summary
        summary = data.get("discovery_summary")
        if not isinstance(summary, dict):
            raise ValueError("discovery_summary must be an object")
        
        summary_required = ["strongest_patterns", "emerging_opportunities", "confidence_level", "learning_progress", "total_segments"]
        missing = [f for f in summary_required if f not in summary]
        if missing:
            raise ValueError(f"Missing required fields in discovery_summary: {missing}")
        
        # Type checks
        if not isinstance(summary["strongest_patterns"], list):
            raise ValueError("strongest_patterns must be an array")
        if not isinstance(summary["emerging_opportunities"], list):
            raise ValueError("emerging_opportunities must be an array")
        if not isinstance(summary["confidence_level"], str):
            raise ValueError("confidence_level must be a string")
        if not isinstance(summary["learning_progress"], str):
            raise ValueError("learning_progress must be a string")
        
        return data
    except Exception as e:
        raise ValueError(f"Invalid LLM response format: {str(e)}")

def prepare_data(state):
    """Prepare and clean lead data"""
    print("\n=== prepare_data Step ===")
    print("Input state keys:", state.keys())
    
    # Get raw data
    raw_leads = state.get("lead_data", [])
    print("Clean data length:", len(raw_leads))
    
    # Clean and normalize leads
    clean_leads = []
    for lead in raw_leads:
        clean_lead = {
            "lead_id": str(lead.get("lead_id", "")),
            "visits": int(lead.get("visits", 0)),
            "time_on_site": float(lead.get("time_on_site", 0.0)),
            "pages_per_visit": float(lead.get("pages_per_visit", 0.0)),
            "converted": bool(lead.get("converted", False)),
            "lead_source": str(lead.get("lead_source", "")),
            "region": str(lead.get("region", "")),
            "company": str(lead.get("company", "")),
            "title": str(lead.get("title", "")),
            "industry": str(lead.get("industry", "Unknown")),
            "company_size": str(lead.get("company_size", "Unknown")),
            "engagement_score": float(lead.get("engagement_score", 0.0))
        }
        clean_leads.append(clean_lead)
    
    if len(clean_leads) > 0:
        print("Sample clean record:", json.dumps(clean_leads[0], indent=2))
    
    return {
        **state,
        "lead_data": clean_leads,
        "status": "data_prepared"
    }

def analyze_patterns(state):
    """Analyze patterns using basic stats - no LLM needed"""
    print("\n=== analyze_patterns Step ===")
    print("Lead data type:", type(state.get("lead_data")))
    print("Lead data length:", len(state.get("lead_data", [])))
    print("Analyzing lead behaviors...")
    
    leads = state.get("lead_data", [])
    if not leads:
        return {
            **state,
            "status": "patterns_analyzed",
            "lead_segments": [],
            "pattern_stats": {}
        }
    
    # Create segments by source
    sources = set(lead["lead_source"] for lead in leads)
    print(f"Found {len(sources)} unique lead sources")
    
    segments = []
    for source in sources:
        source_leads = [l for l in leads if l["lead_source"] == source]
        if source_leads:
            segments.append({
                "name": f"source_{source}",
                "leads": source_leads,
                "size": len(source_leads),
                "avg_visits": sum(l["visits"] for l in source_leads) / len(source_leads),
                "avg_time": sum(l["time_on_site"] for l in source_leads) / len(source_leads),
                "conversion_rate": len([l for l in source_leads if l["converted"]]) / len(source_leads)
            })
            print(f"Created segment for source {source} with {len(source_leads)} leads")
    
    print(f"Created {len(segments)} segments")
    
    return {
        **state,
        "status": "patterns_analyzed",
        "lead_segments": segments
    }

def generate_insights(state, llm=None, prompt_templates=None):
    """Generate insights from lead data using LLM.
    
    Args:
        state (dict): Current workflow state containing:
            - lead_data: List of processed leads
            - sales_data: Optional sales performance data
            - lead_segments: List of analyzed segments
            - status: Current workflow status
        llm: Optional LLM instance
        prompt_templates: Optional prompt templates
            
    Returns:
        dict: Updated state with insights and discovery summary
    """
    if not llm or not prompt_templates:
        return {
            **state,
            "status": "completed",
            "insights": [],
            "discovery_summary": {
                "strongest_patterns": [],
                "emerging_opportunities": [],
                "confidence_level": "low",
                "learning_progress": "Missing LLM or prompts",
                "total_segments": len(state.get("lead_segments", []))
            }
        }
    
    try:
        # Format data for prompt
        lead_data = json.dumps(state.get("lead_data", []), indent=2)
        sales_data = json.dumps(state.get("sales_data", []), indent=2)
        confidence = state.get("confidence_score", 0.7)
        
        # Generate insights using LLM
        print("\n=== Generating Insights ===")
        prompt = prompt_templates["generate_insights"].format(
            lead_data=lead_data,
            sales_data=sales_data,
            confidence_score=confidence
        )
        
        # Get LLM response
        response = llm.generate_content(prompt)
        response_text = response.text.strip()
        
        # Handle markdown code blocks
        if response_text.startswith("```"):
            start = response_text.find("\n") + 1
            end = response_text.rfind("```")
            if end > start:
                response_text = response_text[start:end].strip()
                if response_text.startswith("json\n"):
                    response_text = response_text[5:].strip()
        
        # Parse and validate response
        result = json.loads(response_text)
        
        # Add total_segments if missing
        if "total_segments" not in result["discovery_summary"]:
            result["discovery_summary"]["total_segments"] = len(state.get("lead_segments", []))
        
        return {
            **state,
            "status": "completed",
            **result
        }
        
    except Exception as e:
        print(f"Error in generate_insights: {str(e)}")
        return {
            **state,
            "status": "completed",
            "insights": [],
            "discovery_summary": {
                "strongest_patterns": [],
                "emerging_opportunities": [],
                "confidence_level": "low",
                "learning_progress": f"Error generating insights: {str(e)}",
                "total_segments": len(state.get("lead_segments", []))
            }
        }

def create_lead_research_graph(llm, prompt_templates):
    """Create the LangGraph workflow for lead research"""
    print("\n=== Creating LangGraph Workflow ===")
    
    def generate_insights_with_llm(state):
        """Wrapper to pass LLM to generate_insights"""
        return generate_insights(state, llm, prompt_templates)
    
    # Create workflow
    workflow = StateGraph(state_schema=Dict[str, Any])
    
    # Add nodes
    workflow.add_node("prepare_data", prepare_data)
    workflow.add_node("analyze_patterns", analyze_patterns)
    workflow.add_node("generate_insights", generate_insights_with_llm)
    
    # Define edges
    workflow.add_edge("prepare_data", "analyze_patterns")
    workflow.add_edge("analyze_patterns", "generate_insights")
    
    # Set entry and end points
    workflow.set_entry_point("prepare_data")
    workflow.set_finish_point("generate_insights")
    
    print(f"Workflow created with nodes: {workflow.nodes}")
    return workflow.compile()