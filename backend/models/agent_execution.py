from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime
from db.database import Base


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    agent_name = Column(String, nullable=False)
    status = Column(String, default="completed")
    execution_time_ms = Column(Float, nullable=True)
    session_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
