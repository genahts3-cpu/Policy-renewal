from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from models.policy import Policy
from models.claim import Claim
from schemas.schemas import PolicyResponse, ClaimResponse
from services.auth_service import get_current_customer

router = APIRouter()


@router.get("/", response_model=list[PolicyResponse])
async def get_my_policies(current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    return db.query(Policy).filter(Policy.customer_id == current.id).all()


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: int, current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if not current.is_admin and policy.customer_id != current.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return policy


@router.get("/{policy_id}/claims", response_model=list[ClaimResponse])
async def get_policy_claims(policy_id: int, current: Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy or (not current.is_admin and policy.customer_id != current.id):
        raise HTTPException(status_code=404, detail="Policy not found")
    return db.query(Claim).filter(Claim.policy_id == policy_id).all()
