import logging
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from services.llm_service import get_llm

logger = logging.getLogger(__name__)


class RenewalRecommendation(BaseModel):
    should_renew: bool
    renewal_probability: float
    recommended_premium: float
    key_reasons: list[str]
    personalized_message: str
    risk_factors: list[str]
    benefits_highlighted: list[str]


RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert insurance renewal advisor. Analyze the customer profile and policy data to generate a personalized renewal recommendation.

Consider:
- Customer age and life stage
- Policy type and coverage adequacy
- Claims history (frequency and amounts)
- Risk profile
- Premium affordability
- Policy expiry urgency

Return a JSON object with these exact fields:
- should_renew: boolean
- renewal_probability: float between 0 and 1
- recommended_premium: float (annual premium in USD)
- key_reasons: list of strings (2-4 reasons)
- personalized_message: string (2-3 sentences, warm and professional)
- risk_factors: list of strings (1-3 risks if not renewing)
- benefits_highlighted: list of strings (2-3 benefits of renewing)

Respond ONLY with valid JSON."""),
    ("human", """Customer Profile:
{customer_context}

Policy Details:
- Policy Number: {policy_number}
- Type: {policy_type}
- Current Premium: ${current_premium}/year
- Coverage: ${coverage_amount}
- Expires: {end_date}
- Status: {status}

Claims History: {claims_summary}
Days Until Expiry: {days_until_expiry}"""),
])


async def renewal_recommendation_agent(
    customer_context: str,
    policy_number: str,
    policy_type: str,
    current_premium: float,
    coverage_amount: float,
    end_date: str,
    status: str,
    claims_summary: str,
    days_until_expiry: int,
) -> RenewalRecommendation:
    try:
        llm = get_llm(temperature=0.4)
        structured_llm = llm.with_structured_output(RenewalRecommendation)
        chain = RECOMMENDATION_PROMPT | structured_llm
        result = await chain.ainvoke({
            "customer_context": customer_context,
            "policy_number": policy_number,
            "policy_type": policy_type,
            "current_premium": current_premium,
            "coverage_amount": coverage_amount,
            "end_date": end_date,
            "status": status,
            "claims_summary": claims_summary,
            "days_until_expiry": days_until_expiry,
        })
        logger.info(f"Recommendation for {policy_number}: renew={result.should_renew}, prob={result.renewal_probability}")
        return result
    except Exception as e:
        logger.error(f"Recommendation agent failed: {e}")
        return RenewalRecommendation(
            should_renew=True,
            renewal_probability=0.75,
            recommended_premium=round(current_premium * 1.05, 2),
            key_reasons=["Policy expiring soon", "Continuous coverage recommended"],
            personalized_message=f"Your {policy_type} policy is expiring soon. We recommend renewing to maintain your coverage and avoid any gaps.",
            risk_factors=["Coverage gap risk if not renewed"],
            benefits_highlighted=["Continuous protection", "No re-qualification needed"],
        )
