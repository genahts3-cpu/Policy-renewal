import logging
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from models.policy import Policy
from models.renewal import Renewal
from models.claim import Claim
from schemas.schemas import RenewalResponse, RenewalCreate
from services.auth_service import get_current_customer
from services.rate_limiter import check_rate_limit
from services.audit_service import write_audit_log
from agents.renewal_recommendation_agent import renewal_recommendation_agent
from agents.customer_memory_agent import customer_memory_agent
from agents.notification_agent import notification_agent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[RenewalResponse])
async def get_my_renewals(current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    return db.query(Renewal).filter(Renewal.customer_id == current.id).all()


@router.post("/recommend/{policy_id}", response_model=RenewalResponse)
async def get_renewal_recommendation(
    policy_id: int,
    request: Request,
    current: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    check_rate_limit(current.id)
    policy = db.query(Policy).filter(Policy.id == policy_id, Policy.customer_id == current.id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    memory = await customer_memory_agent(current.id, db)
    claims = db.query(Claim).filter(Claim.customer_id == current.id).all()
    claims_summary = f"{len(claims)} total, {len([c for c in claims if c.status == 'approved'])} approved"

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

    renewal = Renewal(
        policy_id=policy.id,
        customer_id=current.id,
        renewal_date=date.today().isoformat(),
        new_premium=rec.recommended_premium / 83,
        new_end_date=(date.today() + timedelta(days=365)).isoformat(),
        status="pending" if rec.renewal_probability >= 0.60 else "needs_review",
        recommendation_score=rec.renewal_probability,
        recommendation_reason=", ".join(rec.key_reasons),
        ai_recommendation=rec.personalized_message if rec.renewal_probability >= 0.60
            else "Needs Human Review — confidence below threshold.",
    )
    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    write_audit_log(
        db=db, user_id=current.id, agent_name="RenewalAgent",
        action="recommend", question=policy.policy_number,
        response=f"score={rec.renewal_probability:.2f}", status="success",
        ip_address=request.client.host if request.client else None,
    )
    return renewal


@router.post("/{renewal_id}/confirm", response_model=RenewalResponse)
async def confirm_renewal(
    renewal_id: int,
    current: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    renewal = db.query(Renewal).filter(Renewal.id == renewal_id, Renewal.customer_id == current.id).first()
    if not renewal:
        raise HTTPException(status_code=404, detail="Renewal not found")
    if renewal.status == "completed":
        raise HTTPException(status_code=400, detail="Already renewed")

    policy = db.query(Policy).filter(Policy.id == renewal.policy_id).first()
    renewal.status = "completed"
    renewal.completed_at = datetime.utcnow()
    policy.status = "renewed"
    policy.premium_amount = renewal.new_premium
    policy.end_date = renewal.new_end_date
    db.commit()

    await notification_agent(
        db=db,
        customer_id=current.id,
        customer_name=current.full_name,
        policy_number=policy.policy_number,
        policy_type=policy.policy_type,
        end_date=renewal.new_end_date,
        recommended_premium=renewal.new_premium * 83,
        key_message="Your policy has been successfully renewed!",
        channels=["in_app"],
    )

    db.refresh(renewal)
    return renewal


@router.post("/{renewal_id}/decline", response_model=RenewalResponse)
async def decline_renewal(
    renewal_id: int,
    current: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    renewal = db.query(Renewal).filter(Renewal.id == renewal_id, Renewal.customer_id == current.id).first()
    if not renewal:
        raise HTTPException(status_code=404, detail="Renewal not found")
    renewal.status = "declined"
    db.commit()
    db.refresh(renewal)
    return renewal
