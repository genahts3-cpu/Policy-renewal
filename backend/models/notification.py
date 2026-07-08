from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    channel = Column(String, nullable=False)  # email, sms, whatsapp, in_app
    subject = Column(String)
    message = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, sent, failed
    is_read = Column(Boolean, default=False)
    policy_number = Column(String)
    notification_type = Column(String)  # renewal_reminder, recommendation, confirmation
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)

    customer = relationship("Customer", back_populates="notifications")
