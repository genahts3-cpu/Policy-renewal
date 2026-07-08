from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from schemas.schemas import ChatMessage, ChatResponse
from services.auth_service import get_current_customer
from workflows.orchestrator import run_agent_workflow

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    result = await run_agent_workflow(
        customer_id=current.id,
        message=message.message,
        db=db,
        session_id=message.session_id,
    )
    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        session_id=result["session_id"],
        sources=result.get("sources", []),
    )
