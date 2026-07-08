from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    renewal_date = Column(String)
    new_premium = Column(Float)
    new_end_date = Column(String)
    status = Column(String, default="pending")  # pending, completed, declined
    recommendation_score = Column(Float)
    recommendation_reason = Column(Text)
    ai_recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    policy = relationship("Policy", back_populates="renewals")
