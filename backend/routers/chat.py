import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from schemas.schemas import ChatMessage, ChatResponse
from services.auth_service import get_current_customer
from services.guardrail_service import check_prompt_injection, check_off_topic
from services.rate_limiter import check_rate_limit
from services.audit_service import write_audit_log
from workflows.orchestrator import run_agent_workflow

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    request: Request,
    current: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    check_rate_limit(current.id)

    guard = check_prompt_injection(message.message)
    if not guard["safe"]:
        write_audit_log(
            db=db, user_id=current.id, agent_name="GuardrailService",
            action="chat", question=message.message, response=guard["reason"],
            status="blocked", ip_address=request.client.host if request.client else None,
        )
        return ChatResponse(
            response="Your message was flagged by our security system. Please rephrase your question.",
            intent="blocked", session_id=message.session_id or "blocked", sources=[],
        )

    off_topic = check_off_topic(message.message)
    if not off_topic["safe"]:
        write_audit_log(
            db=db, user_id=current.id, agent_name="GuardrailService",
            action="chat", question=message.message, response="off_topic",
            status="blocked", ip_address=request.client.host if request.client else None,
        )
        return ChatResponse(
            response="I'm your insurance assistant and can only help with policy, renewal, and coverage questions. Please ask something related to your insurance.",
            intent="off_topic", session_id=message.session_id or "blocked", sources=[],
        )

    start = time.time()
    result = await run_agent_workflow(
        customer_id=current.id,
        message=message.message,
        db=db,
        session_id=message.session_id,
    )
    elapsed_ms = (time.time() - start) * 1000

    write_audit_log(
        db=db,
        user_id=current.id,
        agent_name="ChatOrchestrator",
        action="chat",
        question=message.message,
        retrieved_documents=", ".join(result.get("sources", [])),
        response=result["response"][:500],
        status="success",
        ip_address=request.client.host if request.client else None,
    )

    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        session_id=result["session_id"],
        sources=result.get("sources", []),
    )
