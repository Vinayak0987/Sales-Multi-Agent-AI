from typing import Dict, List, Any
import pandas as pd
import json
from langgraph_nodes.lead_research_node import create_lead_research_graph
from prompts.lead_research_prompts import lead_research_prompts

class LeadResearchAgent:
    def __init__(self, llm):
        self.llm = llm
        self.leads_data = None
        self.sales_pipeline = None
        
    def load_data(self, leads_path: str, sales_path: str = None):
        """Load the necessary datasets for lead research"""
        print("\n=== Loading Data ===")
        self.leads_data = pd.read_csv(leads_path)
        print(f"Loaded leads data shape: {self.leads_data.shape}")
        print(f"Leads data columns: {self.leads_data.columns.tolist()}")
        
        # Load sales pipeline if available
        if sales_path:
            try:
                self.sales_pipeline = pd.read_csv(sales_path)
                print(f"Loaded sales data shape: {self.sales_pipeline.shape}")
                print(f"Sales data columns: {self.sales_pipeline.columns.tolist()}")
            except:
                print("Sales pipeline data unavailable or could not be loaded")
    
    def _validate_data(self):
        """Validate and prepare data for the workflow"""
        # Convert leads to list format
        leads_list = []
        if self.leads_data is not None:
            for _, row in self.leads_data.iterrows():
                lead = {
                    'visits': int(row.get('visits', 0)),
                    'time_on_site': float(row.get('time_on_site', 0.0)),
                    'pages_per_visit': float(row.get('pages_per_visit', 0.0)),
                    'converted': bool(row.get('converted', False)),
                    'lead_source': str(row.get('lead_source', '')),
                    'region': str(row.get('region', '')),
                    'company': str(row.get('company', '')),
                    'title': str(row.get('title', ''))
                }
                leads_list.append(lead)
                
        # Convert sales to list format
        sales_list = []
        if self.sales_pipeline is not None:
            for _, row in self.sales_pipeline.iterrows():
                sale = {
                    'opportunity_id': str(row.get('opportunity_id', '')),
                    'deal_stage': str(row.get('deal_stage', '')),
                    'close_value': float(row.get('close_value', 0.0)),
                    'company': str(row.get('company', '')),
                    'lead_id': str(row.get('lead_id', '')),
                    'close_date': str(row.get('close_date', '')),
                    'engage_date': str(row.get('engage_date', ''))
                }
                sales_list.append(sale)
                
        return leads_list, sales_list
    
    def process_task(self, task):
        """Process a lead research task using LangGraph workflow"""
        print("\n=== Processing Lead Research Task ===")
        
        # Step 1: Validate data
        leads_list, sales_list = self._validate_data()
        
        # Step 2: Prepare initial state
        initial_state = {
            "lead_data": leads_list,
            "sales_data": sales_list,
            "confidence_score": 0.7,
            "llm": self.llm,
            "prompt_templates": lead_research_prompts
        }
        
        # Step 3: Get our existing workflow
        workflow = create_lead_research_graph(self.llm, lead_research_prompts)
        
        # Step 4: Run the workflow
        final_state = workflow.invoke(initial_state)
        
        # Step 5: Return results
        if 'insights' in final_state:
            # Format insights for interpretation
            insights = final_state['insights']
            insights_text = ""
            for insight in insights:
                insights_text += f"""Pattern: {insight['pattern']}
Evidence:
- Conversion Rate: {insight['evidence']['conversion_rate']:.1%}
- Sample Size: {insight['evidence']['sample_size']}
- Key Indicators: {', '.join(insight['evidence']['key_indicators'])}
Reasoning: {insight['reasoning']}
Learning: {insight['learning']}

"""
            
            # Have the LLM interpret the insights
            interpretation_prompt = lead_research_prompts["interpret_insights"].format(
                insights=insights_text
            )
            
            print("\n=== Interpreting Insights ===")
            response = self.llm.generate_content(interpretation_prompt)
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
            try:
                result = json.loads(response_text)
                if not isinstance(result.get("lead_quality_indicators"), dict):
                    raise ValueError("lead_quality_indicators must be an object")
                if not isinstance(result.get("engagement_recommendations"), list):
                    raise ValueError("engagement_recommendations must be an array")
                return json.dumps(result)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing interpretation: {str(e)}")
                return "Error interpreting insights"
        else:
            return "No insights were generated from the lead analysis."