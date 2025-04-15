"""Intent Qualifier Prompts

This module contains prompts for the Intent Qualifier Agent.
Focuses on identifying high-intent leads based on behavior patterns.
"""

# Simple prompt for generating insights from lead behavior
generate_insights_prompt = """Analyze the following lead behavior data and identify purchase intent signals.
Lead Data: {lead_data}
Email Interactions: {email_data}

Focus on:
1. Engagement patterns indicating serious purchase intent
2. Key behaviors that differentiate high-intent leads
3. Specific recommendations for sales follow-up

IMPORTANT: Return a valid JSON object with this exact structure. Do not include any other text or formatting.
{{
  "intent_signals": [
    {{
      "signal": "signal description",
      "strength": "high/medium/low",
      "evidence": "supporting data points"
    }}
  ],
  "recommendations": [
    {{
      "action": "recommended action",
      "priority": "high/medium/low",
      "reasoning": "why this action"
    }}
  ]
}}"""

# Export prompts
intent_qualifier_prompts = {
    "generate_insights": generate_insights_prompt
}