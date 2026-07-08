from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    policy_type = Column(String, nullable=False)  # life, health, auto, home, travel
    coverage_amount = Column(Float, nullable=False)
    premium_amount = Column(Float, nullable=False)
    deductible = Column(Float, default=0.0)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    status = Column(String, default="active")  # active, expired, cancelled, renewed
    description = Column(Text)
    beneficiary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="policies")
    renewals = relationship("Renewal", back_populates="policy")
