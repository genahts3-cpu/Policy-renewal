import logging
from typing import TypedDict
from langchain.prompts import ChatPromptTemplate
from services.llm_service import get_llm

logger = logging.getLogger(__name__)

SUPPORT_KEYWORDS = [
    "talk to someone", "speak with", "human", "agent", "representative",
    "callback", "call me", "support", "help me", "need assistance",
    "don't understand", "confused", "explain", "clarify", "questions about",
    "need help", "want to talk", "connect me", "schedule", "appointment",
    "meet", "consultation", "advisor", "expert",
]

SUPPORT_DETECTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a support detection agent for an insurance company.
Determine if the customer message requires human support assistance.

Return ONLY a JSON object with this exact format:
{{"needsSupport": true/false, "reason": "brief reason", "urgency": "low/medium/high"}}

Trigger needsSupport=true when customer:
- Asks to speak with a human, agent, or representative
- Requests a callback or appointment
- Expresses confusion or frustration
- Has complex questions about claims or renewals
- Explicitly asks for support or help from a person
- Wants to schedule a meeting or consultation

Do NOT trigger for simple AI-answerable questions about policy details."""),
    ("human", "{message}"),
])


class SupportDetection(TypedDict):
    needs_support: bool
    reason: str
    urgency: str


def _keyword_check(message: str) -> bool:
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in SUPPORT_KEYWORDS)


async def support_detection_agent(message: str) -> SupportDetection:
    # Fast keyword check first
    if _keyword_check(message):
        logger.info(f"Support needed (keyword match): {message[:80]}")
        return SupportDetection(needs_support=True, reason="Customer requested human assistance.", urgency="medium")

    try:
        llm = get_llm(temperature=0.1)
        chain = SUPPORT_DETECTION_PROMPT | llm
        result = await chain.ainvoke({"message": message})
        import json, re
        text = result.content.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return SupportDetection(
                needs_support=bool(data.get("needsSupport", False)),
                reason=data.get("reason", ""),
                urgency=data.get("urgency", "medium"),
            )
    except Exception as e:
        logger.warning(f"Support detection LLM failed: {e}")

    return SupportDetection(needs_support=False, reason="", urgency="low")
