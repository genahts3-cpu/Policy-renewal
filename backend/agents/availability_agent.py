import json
import logging
from typing import List, Dict, TypedDict, Optional
from sqlalchemy.orm import Session
from models.support_user import SupportUser
from services.mcp.calendar_mcp_client import get_calendar_tools

logger = logging.getLogger(__name__)


class AvailabilityResult(TypedDict):
    recommended_slots: List[Dict]
    support_user_id: int
    support_user_name: str
    support_user_email: str


async def availability_agent(
    customer_email: str,
    db: Session,
    support_user_id: Optional[int] = None,
    duration_minutes: int = 30,
) -> AvailabilityResult:
    """
    Uses the Google Calendar MCP server to find available slots for a support agent.
    """
    # Resolve support user from DB
    if support_user_id:
        support_user = db.query(SupportUser).filter(SupportUser.id == support_user_id).first()
    else:
        support_user = db.query(SupportUser).filter(SupportUser.status == "available").first()

    if not support_user:
        support_user = _ensure_default_support_user(db)

    support_email = support_user.calendar_email or support_user.email

    # Call get_available_slots via MCP
    slots = await _call_get_slots_via_mcp(support_email, duration_minutes)

    logger.info(f"MCP returned {len(slots)} slots for {support_email}")
    return AvailabilityResult(
        recommended_slots=slots,
        support_user_id=support_user.id,
        support_user_name=support_user.name,
        support_user_email=support_email,
    )


async def _call_get_slots_via_mcp(support_email: str, duration_minutes: int) -> List[Dict]:
    """Invoke the get_available_slots MCP tool and return parsed slots."""
    tools = await get_calendar_tools()
    tool = next((t for t in tools if t.name == "get_available_slots"), None)

    if not tool:
        logger.warning("get_available_slots MCP tool not found, using fallback")
        return _fallback_slots(duration_minutes)

    try:
        raw = await tool.ainvoke({
            "support_email": support_email,
            "days_ahead": 3,
            "duration_minutes": duration_minutes,
        })
        # Tool returns a JSON string or a list
        if isinstance(raw, str):
            slots = json.loads(raw)
        else:
            slots = raw
        return slots if slots else _fallback_slots(duration_minutes)
    except Exception as e:
        logger.warning(f"MCP get_available_slots failed: {e}")
        return _fallback_slots(duration_minutes)


def _ensure_default_support_user(db: Session) -> SupportUser:
    try:
        user = SupportUser(
            name="Support Team",
            email="support@insurance.com",
            calendar_email="support@insurance.com",
            department="Customer Support",
            status="available",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        # Return a transient object so the rest of the flow doesn't crash
        return SupportUser(
            id=0,
            name="Support Team",
            email="support@insurance.com",
            calendar_email="support@insurance.com",
            department="Customer Support",
            status="available",
        )


def _fallback_slots(duration_minutes: int = 30) -> List[Dict]:
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    slots = []
    for offset in [timedelta(hours=2), timedelta(days=1, hours=1), timedelta(days=1, hours=5)]:
        start = now + offset
        if start.hour < 9:
            start = start.replace(hour=9)
        elif start.hour >= 17:
            start = (start + timedelta(days=1)).replace(hour=9)
        end = start + timedelta(minutes=duration_minutes)
        slots.append({
            "start": start.isoformat(),
            "end": end.isoformat(),
            "display": start.strftime("%d %b %Y, %I:%M %p"),
        })
    return slots
