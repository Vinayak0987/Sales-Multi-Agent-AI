"""Email Strategy Prompts"""

email_strategy_prompts = {
    "craft_email": """You are an AI sales assistant helping craft personalized emails to qualified leads.

CONTEXT:
Lead Data: {lead}
Intent Signals: {intent_signals}
Company Info: {company_info}

TASK:
Craft a personalized email that:
1. Demonstrates understanding of their needs based on intent signals
2. Highlights relevant value props
3. Includes a clear call to action

OUTPUT FORMAT:
Return a strictly valid JSON object with exactly these keys:
{{
    "subject": "Email subject line",
    "personalization_factors": ["List of personalization factors used"],
    "email_preview": "Full email body"
}}

GUIDELINES:
- Keep subject line short and compelling
- Make body concise (3-4 paragraphs max)
- Use natural, conversational tone
- Focus on their specific needs/pain points
- End with clear next steps
- NO PLACEHOLDERS. Skip names if not provided.
- DO NOT wrap your response in markdown blocks!
"""
}
