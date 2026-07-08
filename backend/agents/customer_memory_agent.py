import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.customer import Customer
from models.policy import Policy
from models.claim import Claim
from models.conversation import Conversation

logger = logging.getLogger(__name__)


class CustomerMemory:
    def __init__(self, customer: Customer, policies: List[Policy], claims: List[Claim], history: List[Dict]):
        self.customer = customer
        self.policies = policies
        self.claims = claims
        self.history = history

    def to_context_string(self) -> str:
        lines = [
            f"Customer: {self.customer.full_name}",
            f"Age: {self.customer.age or 'Unknown'}",
            f"Occupation: {self.customer.occupation or 'Unknown'}",
            f"Risk Profile: {self.customer.risk_profile}",
            f"Active Policies: {len([p for p in self.policies if p.status == 'active'])}",
            f"Total Claims: {len(self.claims)}",
            f"Approved Claims: {len([c for c in self.claims if c.status == 'approved'])}",
        ]
        if self.policies:
            lines.append("\nPolicies:")
            for p in self.policies:
                premium_inr = p.premium_amount * 83
                coverage_inr = p.coverage_amount * 83
                lines.append(f"  - {p.policy_number}: {p.policy_type} | ₹{premium_inr:,.0f}/yr | Coverage: ₹{coverage_inr:,.0f} | Status: {p.status} | Expires: {p.end_date}")
        if self.history:
            lines.append(f"\nRecent conversation turns: {len(self.history)}")
        return "\n".join(lines)


async def customer_memory_agent(customer_id: int, db: Session) -> CustomerMemory:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError(f"Customer {customer_id} not found")

    policies = db.query(Policy).filter(Policy.customer_id == customer_id).all()
    claims = db.query(Claim).filter(Claim.customer_id == customer_id).all()

    recent_convos = (
        db.query(Conversation)
        .filter(Conversation.customer_id == customer_id)
        .order_by(Conversation.created_at.desc())
        .limit(10)
        .all()
    )
    history = [{"role": c.role, "content": c.content} for c in reversed(recent_convos)]

    logger.info(f"Loaded memory for customer {customer_id}: {len(policies)} policies, {len(claims)} claims")
    return CustomerMemory(customer=customer, policies=policies, claims=claims, history=history)


def save_conversation(db: Session, customer_id: int, session_id: str, role: str, content: str, intent: str = None, policy_number: str = None):
    convo = Conversation(
        customer_id=customer_id,
        session_id=session_id,
        role=role,
        content=content,
        intent=intent,
        policy_number=policy_number,
    )
    db.add(convo)
    db.commit()
