from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    question = Column(Text, nullable=True)
    retrieved_documents = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    status = Column(String, default="success")
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
