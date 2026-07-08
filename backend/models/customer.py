from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    date_of_birth = Column(String)
    age = Column(Integer)
    occupation = Column(String)
    risk_profile = Column(String, default="medium")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    policies = relationship("Policy", back_populates="customer")
    claims = relationship("Claim", back_populates="customer")
    conversations = relationship("Conversation", back_populates="customer")
    notifications = relationship("Notification", back_populates="customer")
