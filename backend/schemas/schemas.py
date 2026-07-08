from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str
    customer_id: int
    is_admin: bool
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


# Customer
class CustomerCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    address: Optional[str]
    date_of_birth: Optional[str]
    age: Optional[int]
    occupation: Optional[str]
    risk_profile: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Policy
class PolicyResponse(BaseModel):
    id: int
    policy_number: str
    customer_id: int
    policy_type: str
    coverage_amount: float
    premium_amount: float
    deductible: float
    start_date: str
    end_date: str
    status: str
    description: Optional[str]
    beneficiary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Renewal
class RenewalCreate(BaseModel):
    policy_id: int


class RenewalResponse(BaseModel):
    id: int
    policy_id: int
    customer_id: int
    renewal_date: Optional[str]
    new_premium: Optional[float]
    new_end_date: Optional[str]
    status: str
    recommendation_score: Optional[float]
    recommendation_reason: Optional[str]
    ai_recommendation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Claim
class ClaimResponse(BaseModel):
    id: int
    claim_number: str
    customer_id: int
    policy_id: int
    claim_type: Optional[str]
    amount: Optional[float]
    status: str
    description: Optional[str]
    filed_date: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Chat
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    policy_number: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str]
    session_id: str
    sources: Optional[List[str]] = []


# Notification
class NotificationResponse(BaseModel):
    id: int
    customer_id: int
    channel: str
    subject: Optional[str]
    message: str
    status: str
    is_read: bool
    policy_number: Optional[str]
    notification_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Knowledge
class KnowledgeUploadResponse(BaseModel):
    message: str
    chunks_added: int
    filename: str


# Admin Stats
class AdminStats(BaseModel):
    total_customers: int
    total_policies: int
    active_policies: int
    expired_policies: int
    total_renewals: int
    completed_renewals: int
    pending_renewals: int
    total_claims: int
    renewal_rate: float


# Audit Log
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    agent_name: str
    action: str
    question: Optional[str]
    retrieved_documents: Optional[str]
    response: Optional[str]
    status: str
    ip_address: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# Agent Execution
class AgentExecutionResponse(BaseModel):
    id: int
    user_id: Optional[int]
    agent_name: str
    status: str
    execution_time_ms: Optional[float]
    session_id: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# Guardrail
class GuardrailStats(BaseModel):
    total_checks: int
    blocked_requests: int
    safe_requests: int
    block_rate: float
