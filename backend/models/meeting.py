from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    support_user_id = Column(Integer, ForeignKey("support_users.id"), nullable=False)
    subject = Column(String, nullable=False)
    description = Column(Text)
    meeting_type = Column(String, default="google_meet")
    meeting_link = Column(String)
    google_event_id = Column(String)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, rescheduled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer")
    support_user = relationship("SupportUser")
