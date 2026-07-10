import logging
from typing import Optional
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from services.llm_service import get_llm

logger = logging.getLogger(__name__)


class GoalUnderstanding(BaseModel):
    intent: str
    policy_number: Optional[str] = None
    urgency: str = "normal"
    customer_name: Optional[str] = None
    summary: str


INTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an insurance assistant. Analyze the customer message and extract structured information.

Return a JSON object with these exact fields:
- intent: one of [renew_policy, ask_question, check_status, get_recommendation, general_chat, view_policy]
- policy_number: policy number if mentioned (like POL-XXXXX), or null
- urgency: one of [low, normal, high, critical]
- customer_name: customer name if mentioned, or null
- summary: one sentence summary of what the customer wants

Use "ask_question" for ANY question about coverage, benefits, claims, maternity, exclusions, deductibles, terms, or policy details.
Use "general_chat" only for greetings, meta questions, or truly general conversation.

Respond ONLY with valid JSON, no markdown, no explanation."""),
    ("human", "Customer message: {message}\nCustomer name: {customer_name}"),
])


async def goal_understanding_agent(message: str, customer_name: str = "") -> GoalUnderstanding:
    try:
        llm = get_llm(temperature=0.1)
        structured_llm = llm.with_structured_output(GoalUnderstanding)
        chain = INTENT_PROMPT | structured_llm
        result = await chain.ainvoke({"message": message, "customer_name": customer_name})
        logger.info(f"Goal understood: intent={result.intent}, urgency={result.urgency}")
        return result
    except Exception as e:
        logger.error(f"Goal understanding failed: {e}")
        return GoalUnderstanding(
            intent="general_chat",
            urgency="normal",
            summary=message[:100],
        )
