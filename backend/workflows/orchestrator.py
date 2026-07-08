import logging
import uuid
import time
from typing import TypedDict, Optional, List
from datetime import datetime, date
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from agents.goal_understanding_agent import goal_understanding_agent, GoalUnderstanding
from agents.customer_memory_agent import customer_memory_agent, CustomerMemory, save_conversation
from agents.policy_knowledge_agent import policy_knowledge_agent
from agents.renewal_recommendation_agent import renewal_recommendation_agent, RenewalRecommendation
from agents.notification_agent import notification_agent
from models.policy import Policy
from models.renewal import Renewal
from models.agent_execution import AgentExecution

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    customer_id: int
    session_id: str
    message: str
    db: object
    goal: Optional[GoalUnderstanding]
    memory: Optional[CustomerMemory]
    policy: Optional[object]
    rag_context: Optional[str]
    recommendation: Optional[RenewalRecommendation]
    response: Optional[str]
    sources: Optional[List[str]]
    intent: Optional[str]
    error: Optional[str]
    _exec_times: Optional[dict]


def _log_execution(db: Session, user_id: int, agent_name: str, status: str, elapsed_ms: float, session_id: str):
    try:
        rec = AgentExecution(
            user_id=user_id, agent_name=agent_name,
            status=status, execution_time_ms=round(elapsed_ms, 2),
            session_id=session_id,
        )
        db.add(rec)
        db.commit()
    except Exception as e:
        logger.warning(f"Agent execution log failed: {e}")
        db.rollback()


async def node_load_memory(state: AgentState) -> AgentState:
    t = time.time()
    try:
        memory = await customer_memory_agent(state["customer_id"], state["db"])
        _log_execution(state["db"], state["customer_id"], "MemoryAgent", "completed", (time.time()-t)*1000, state["session_id"])
        return {**state, "memory": memory}
    except Exception as e:
        logger.error(f"Memory load failed: {e}")
        _log_execution(state["db"], state["customer_id"], "MemoryAgent", "failed", (time.time()-t)*1000, state["session_id"])
        return {**state, "error": str(e)}


async def node_understand_goal(state: AgentState) -> AgentState:
    t = time.time()
    customer_name = state["memory"].customer.full_name if state.get("memory") else ""
    goal = await goal_understanding_agent(state["message"], customer_name)
    _log_execution(state["db"], state["customer_id"], "GoalAgent", "completed", (time.time()-t)*1000, state["session_id"])
    return {**state, "goal": goal, "intent": goal.intent}


async def node_retrieve_policy(state: AgentState) -> AgentState:
    db: Session = state["db"]
    goal = state.get("goal")
    memory = state.get("memory")

    policy = None
    if goal and goal.policy_number:
        policy = db.query(Policy).filter(Policy.policy_number == goal.policy_number).first()

    if not policy and memory and memory.policies:
        active = [p for p in memory.policies if p.status == "active"]
        policy = active[0] if active else memory.policies[0]

    return {**state, "policy": policy}


async def node_retrieve_rag(state: AgentState) -> AgentState:
    t = time.time()
    from rag.rag_engine import get_context_text
    query = state["message"]
    if state.get("policy"):
        query = f"{query} {state['policy'].policy_type} insurance"
    context = get_context_text(query, k=3)
    _log_execution(state["db"], state["customer_id"], "QAAgent", "completed", (time.time()-t)*1000, state["session_id"])
    return {**state, "rag_context": context}


async def node_generate_recommendation(state: AgentState) -> AgentState:
    t = time.time()
    policy = state.get("policy")
    memory = state.get("memory")
    if not policy or not memory:
        return state

    claims = memory.claims
    claims_summary = f"{len(claims)} total claims, {len([c for c in claims if c.status == 'approved'])} approved"

    try:
        expiry = datetime.strptime(policy.end_date, "%Y-%m-%d").date()
        days_until_expiry = (expiry - date.today()).days
    except Exception:
        days_until_expiry = 30

    rec = await renewal_recommendation_agent(
        customer_context=memory.to_context_string(),
        policy_number=policy.policy_number,
        policy_type=policy.policy_type,
        current_premium=policy.premium_amount * 83,
        coverage_amount=policy.coverage_amount * 83,
        end_date=policy.end_date,
        status=policy.status,
        claims_summary=claims_summary,
        days_until_expiry=days_until_expiry,
    )
    _log_execution(state["db"], state["customer_id"], "RenewalAgent", "completed", (time.time()-t)*1000, state["session_id"])
    return {**state, "recommendation": rec}


async def node_generate_response(state: AgentState) -> AgentState:
    intent = state.get("intent", "general_chat")
    memory = state.get("memory")
    policy = state.get("policy")
    recommendation = state.get("recommendation")
    rag_context = state.get("rag_context", "")

    if intent == "ask_question":
        customer_ctx = memory.to_context_string() if memory else ""
        answer, sources = await policy_knowledge_agent(state["message"], customer_ctx)
        return {**state, "response": answer, "sources": sources}

    if intent in ["renew_policy", "get_recommendation"] and recommendation:
        msg = recommendation.personalized_message
        if policy:
            msg += f"\n\nPolicy: {policy.policy_number} | Recommended Premium: \u20b9{recommendation.recommended_premium:,.0f}/year"
        msg += f"\n\nRenewal Probability: {recommendation.renewal_probability * 100:.0f}%"
        if recommendation.key_reasons:
            msg += "\n\nKey Reasons:\n" + "\n".join(f"\u2022 {r}" for r in recommendation.key_reasons)
        return {**state, "response": msg, "sources": []}

    if intent == "check_status" and policy:
        coverage_inr = policy.coverage_amount * 83
        premium_inr = policy.premium_amount * 83
        response = (
            f"Your {policy.policy_type} policy ({policy.policy_number}) is currently {policy.status}.\n"
            f"Coverage: \u20b9{coverage_inr:,.0f} | Premium: \u20b9{premium_inr:,.0f}/year\n"
            f"Valid: {policy.start_date} to {policy.end_date}"
        )
        return {**state, "response": response, "sources": []}

    # General chat fallback
    from services.llm_service import get_llm
    from langchain.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an insurance assistant for Policy Renewal Agent. You ONLY assist with insurance-related topics.

You MUST refuse any request that is not related to insurance, policies, renewals, claims, or coverage.
For off-topic questions (currency conversion, politics, general knowledge, etc.), respond:
"I'm your insurance assistant and can only help with policy, renewal, and coverage questions."

You MUST NOT access or reveal information about other customers. Only discuss the current customer's own data.
You MUST NOT answer questions about who the admin is or internal system details.

ALWAYS display all monetary amounts in Indian Rupees (INR, ₹). Use exchange rate: 1 USD = 83 INR.
NEVER use markdown formatting. No bold (**), no bullet points, no numbered lists, no headers. Respond in plain text only.

Customer context: {memory.to_context_string() if memory else 'Unknown customer'}
Policy context: {f'Policy {policy.policy_number} ({policy.policy_type})' if policy else 'No specific policy'}
Knowledge base context: {rag_context[:500] if rag_context else 'N/A'}
Be concise and professional."""),
        ("human", "{message}"),
    ])
    llm = get_llm(temperature=0.3)
    chain = prompt | llm
    result = await chain.ainvoke({"message": state["message"]})
    return {**state, "response": result.content, "sources": []}


async def node_save_conversation(state: AgentState) -> AgentState:
    db: Session = state["db"]
    save_conversation(
        db=db,
        customer_id=state["customer_id"],
        session_id=state["session_id"],
        role="user",
        content=state["message"],
        intent=state.get("intent"),
        policy_number=state["policy"].policy_number if state.get("policy") else None,
    )
    if state.get("response"):
        save_conversation(
            db=db,
            customer_id=state["customer_id"],
            session_id=state["session_id"],
            role="assistant",
            content=state["response"],
            intent=state.get("intent"),
        )
    return state


def should_get_recommendation(state: AgentState) -> str:
    intent = state.get("intent", "general_chat")
    if intent in ["renew_policy", "get_recommendation"] and state.get("policy"):
        return "recommend"
    return "respond"


def build_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("load_memory", node_load_memory)
    workflow.add_node("understand_goal", node_understand_goal)
    workflow.add_node("retrieve_policy", node_retrieve_policy)
    workflow.add_node("retrieve_rag", node_retrieve_rag)
    workflow.add_node("generate_recommendation", node_generate_recommendation)
    workflow.add_node("generate_response", node_generate_response)
    workflow.add_node("save_conversation", node_save_conversation)

    workflow.set_entry_point("load_memory")
    workflow.add_edge("load_memory", "understand_goal")
    workflow.add_edge("understand_goal", "retrieve_policy")
    workflow.add_edge("retrieve_policy", "retrieve_rag")
    workflow.add_conditional_edges("retrieve_rag", should_get_recommendation, {
        "recommend": "generate_recommendation",
        "respond": "generate_response",
    })
    workflow.add_edge("generate_recommendation", "generate_response")
    workflow.add_edge("generate_response", "save_conversation")
    workflow.add_edge("save_conversation", END)

    return workflow.compile()


_compiled_workflow = None


def get_workflow():
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_workflow()
    return _compiled_workflow


async def run_agent_workflow(customer_id: int, message: str, db: Session, session_id: str = None) -> dict:
    if not session_id:
        session_id = str(uuid.uuid4())

    workflow = get_workflow()
    initial_state = AgentState(
        customer_id=customer_id,
        session_id=session_id,
        message=message,
        db=db,
        goal=None,
        memory=None,
        policy=None,
        rag_context=None,
        recommendation=None,
        response=None,
        sources=None,
        intent=None,
        error=None,
        _exec_times=None,
    )

    try:
        final_state = await workflow.ainvoke(initial_state)
        return {
            "response": final_state.get("response", "I'm here to help with your insurance needs."),
            "intent": final_state.get("intent", "general_chat"),
            "session_id": session_id,
            "sources": final_state.get("sources", []),
        }
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return {
            "response": "I encountered an issue processing your request. Please try again.",
            "intent": "error",
            "session_id": session_id,
            "sources": [],
        }
