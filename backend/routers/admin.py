from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from models.policy import Policy
from models.renewal import Renewal
from models.claim import Claim
from models.audit_log import AuditLog
from models.agent_execution import AgentExecution
from schemas.schemas import (
    AdminStats, CustomerResponse, PolicyResponse, RenewalResponse,
    AuditLogResponse, AgentExecutionResponse, GuardrailStats,
)
from services.auth_service import get_admin_customer

router = APIRouter()


@router.get("/stats", response_model=AdminStats)
async def get_stats(db: Session = Depends(get_db), _: Customer = Depends(get_admin_customer)):
    total_customers = db.query(Customer).count()
    total_policies = db.query(Policy).count()
    active_policies = db.query(Policy).filter(Policy.status == "active").count()
    expired_policies = db.query(Policy).filter(Policy.status == "expired").count()
    total_renewals = db.query(Renewal).count()
    completed_renewals = db.query(Renewal).filter(Renewal.status == "completed").count()
    pending_renewals = db.query(Renewal).filter(Renewal.status == "pending").count()
    total_claims = db.query(Claim).count()
    renewal_rate = (completed_renewals / total_renewals * 100) if total_renewals > 0 else 0.0
    return AdminStats(
        total_customers=total_customers, total_policies=total_policies,
        active_policies=active_policies, expired_policies=expired_policies,
        total_renewals=total_renewals, completed_renewals=completed_renewals,
        pending_renewals=pending_renewals, total_claims=total_claims,
        renewal_rate=renewal_rate,
    )


@router.get("/customers", response_model=list[CustomerResponse])
async def admin_customers(db: Session = Depends(get_db), _: Customer = Depends(get_admin_customer)):
    return db.query(Customer).all()


@router.get("/policies", response_model=list[PolicyResponse])
async def admin_policies(db: Session = Depends(get_db), _: Customer = Depends(get_admin_customer)):
    return db.query(Policy).all()


@router.get("/renewals", response_model=list[RenewalResponse])
async def admin_renewals(db: Session = Depends(get_db), _: Customer = Depends(get_admin_customer)):
    return db.query(Renewal).order_by(Renewal.created_at.desc()).all()


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Customer = Depends(get_admin_customer),
):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()


@router.get("/agent-executions", response_model=list[AgentExecutionResponse])
async def get_agent_executions(
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Customer = Depends(get_admin_customer),
):
    return db.query(AgentExecution).order_by(AgentExecution.timestamp.desc()).limit(limit).all()


@router.get("/guardrail-stats", response_model=GuardrailStats)
async def get_guardrail_stats(db: Session = Depends(get_db), _: Customer = Depends(get_admin_customer)):
    total = db.query(AuditLog).count()
    blocked = db.query(AuditLog).filter(AuditLog.status == "blocked").count()
    safe = total - blocked
    return GuardrailStats(
        total_checks=total,
        blocked_requests=blocked,
        safe_requests=safe,
        block_rate=round((blocked / total * 100), 2) if total > 0 else 0.0,
    )
