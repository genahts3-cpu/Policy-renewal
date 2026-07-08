import logging
from datetime import datetime
from sqlalchemy.orm import Session
from langchain.prompts import ChatPromptTemplate
from models.notification import Notification
from services.llm_service import get_llm

logger = logging.getLogger(__name__)

MESSAGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly insurance communication specialist.
Generate a personalized {channel} message for a policy renewal notification.
Keep it concise, warm, and action-oriented.
For email: start with 'Subject: <subject line>' on the first line, then the message body.
For sms or whatsapp: keep under 160 characters, no subject needed.
For in_app: 1-2 sentences, friendly tone."""),
    ("human", """Customer: {customer_name}
Policy: {policy_number} ({policy_type})
Expiry: {end_date}
Recommended Premium: ₹{recommended_premium}
Key Message: {key_message}
Channel: {channel}"""),
])


async def generate_notification_message(
    channel: str,
    customer_name: str,
    policy_number: str,
    policy_type: str,
    end_date: str,
    recommended_premium: float,
    key_message: str,
) -> tuple[str, str]:
    try:
        llm = get_llm(temperature=0.6)
        chain = MESSAGE_PROMPT | llm
        result = await chain.ainvoke({
            "channel": channel,
            "customer_name": customer_name,
            "policy_number": policy_number,
            "policy_type": policy_type,
            "end_date": end_date,
            "recommended_premium": recommended_premium,
            "key_message": key_message,
        })
        content = result.content.strip()
        subject = ""
        if channel == "email" and content.startswith("Subject:"):
            lines = content.split("\n", 2)
            subject = lines[0].replace("Subject:", "").strip()
            content = "\n".join(lines[1:]).strip()
        return subject, content
    except Exception as e:
        logger.error(f"Notification message generation failed: {e}")
        subject = f"Policy Renewal Reminder - {policy_number}"
        content = f"Dear {customer_name}, your {policy_type} policy {policy_number} expires on {end_date}. Renew now for ₹{recommended_premium:,.0f}/year."
        return subject, content


async def notification_agent(
    db: Session,
    customer_id: int,
    customer_name: str,
    policy_number: str,
    policy_type: str,
    end_date: str,
    recommended_premium: float,
    key_message: str,
    channels: list[str] = None,
) -> list[Notification]:
    if channels is None:
        channels = ["in_app"]

    notifications = []
    for channel in channels:
        subject, message = await generate_notification_message(
            channel=channel,
            customer_name=customer_name,
            policy_number=policy_number,
            policy_type=policy_type,
            end_date=end_date,
            recommended_premium=recommended_premium,
            key_message=key_message,
        )
        notif = Notification(
            customer_id=customer_id,
            channel=channel,
            subject=subject,
            message=message,
            policy_number=policy_number,
            notification_type="renewal_reminder",
            status="sent",
            sent_at=datetime.utcnow(),
        )
        db.add(notif)
        notifications.append(notif)

    db.commit()
    logger.info(f"Created {len(notifications)} notifications for customer {customer_id}")
    return notifications
