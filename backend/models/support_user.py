from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from db.database import Base


class SupportUser(Base):
    __tablename__ = "support_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String, default="Customer Support")
    calendar_email = Column(String)
    status = Column(String, default="available")  # available, busy, offline
    created_at = Column(DateTime, default=datetime.utcnow)
