import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.meeting import Meeting
from models.customer import Customer
from models.support_user import SupportUser
from models.notification import Notification
from services.mcp.calendar_mcp_client import get_calendar_tools
from services.audit_service import write_audit_log

logger = logging.getLogger(__name__)


async def meeting_scheduling_agent(
    customer_id: int,
    support_user_id: int,
    selected_slot: Dict,
    subject: str,
    description: str,
    db: Session,
) -> Dict[str, Any]:
    """Create a Google Calendar event via MCP, persist meeting, send notification."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    support_user = db.query(SupportUser).filter(SupportUser.id == support_user_id).first()

    if not customer or not support_user:
        return {"status": "failed", "error": "Customer or support user not found."}

    try:
        start_dt = datetime.fromisoformat(selected_slot["start"].replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(selected_slot["end"].replace("Z", "+00:00"))
    except Exception as e:
        return {"status": "failed", "error": f"Invalid slot format: {e}"}

    if start_dt < datetime.now(timezone.utc):
        return {"status": "failed", "error": "Cannot schedule meetings in the past."}

    overlap = db.query(Meeting).filter(
        Meeting.customer_id == customer_id,
        Meeting.status == "scheduled",
        Meeting.scheduled_start < end_dt,
        Meeting.scheduled_end > start_dt,
    ).first()
    if overlap:
        return {"status": "failed", "error": "You already have a meeting at this time."}

    support_email = support_user.calendar_email or support_user.email

    # Call create_calendar_event via MCP
    calendar_result = await _call_mcp_tool("create_calendar_event", {
        "subject": subject,
        "description": description,
        "start_iso": start_dt.isoformat(),
        "end_iso": end_dt.isoformat(),
        "customer_email": customer.email,
        "support_email": support_email,
        "customer_name": customer.full_name,
        "support_name": support_user.name,
    })

    meeting = Meeting(
        customer_id=customer_id,
        support_user_id=support_user_id,
        subject=subject,
        description=description,
        meeting_type="google_meet",
        meeting_link=calendar_result.get("meeting_link", ""),
        google_event_id=calendar_result.get("google_event_id", ""),
        scheduled_start=start_dt,
        scheduled_end=end_dt,
        duration_minutes=int((end_dt - start_dt).total_seconds() / 60),
        status="scheduled",
    )
    db.add(meeting)
    db.flush()

    _notify(
        db, customer_id,
        subject=f"Meeting Scheduled: {subject}",
        message=(
            f"Your support meeting has been scheduled.\n"
            f"Representative: {support_user.name}\n"
            f"Date: {start_dt.strftime('%d %b %Y at %I:%M %p')}\n"
            f"Google Meet: {calendar_result.get('meeting_link', 'Link will be shared shortly')}"
        ),
        notification_type="meeting_scheduled",
    )
    db.commit()
    db.refresh(meeting)

    write_audit_log(
        db=db, user_id=customer_id, agent_name="MeetingSchedulingAgent",
        action="schedule_meeting", question=subject,
        response=f"Meeting {meeting.id} scheduled via MCP. Link: {meeting.meeting_link}",
        status="success",
    )

    return {
        "status": "scheduled",
        "meeting_id": meeting.id,
        "meeting_link": meeting.meeting_link,
        "google_event_id": meeting.google_event_id,
        "scheduled_start": start_dt.isoformat(),
        "scheduled_end": end_dt.isoformat(),
        "support_user_name": support_user.name,
    }


async def cancel_meeting_agent(meeting_id: int, customer_id: int, db: Session) -> Dict[str, Any]:
    """Cancel a meeting and call cancel_calendar_event via MCP."""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, Meeting.customer_id == customer_id
    ).first()

    if not meeting:
        return {"status": "failed", "error": "Meeting not found."}
    if meeting.status != "scheduled":
        return {"status": "failed", "error": f"Meeting is already {meeting.status}."}

    if meeting.google_event_id:
        await _call_mcp_tool("cancel_calendar_event", {"google_event_id": meeting.google_event_id})

    meeting.status = "cancelled"
    _notify(
        db, customer_id,
        subject="Meeting Cancelled",
        message=f"Your meeting '{meeting.subject}' on {meeting.scheduled_start.strftime('%d %b %Y at %I:%M %p')} has been cancelled.",
        notification_type="meeting_cancelled",
    )
    db.commit()
    return {"status": "cancelled", "meeting_id": meeting_id}


async def reschedule_meeting_agent(
    meeting_id: int, customer_id: int, new_slot: Dict, db: Session
) -> Dict[str, Any]:
    """Reschedule a meeting and call reschedule_calendar_event via MCP."""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, Meeting.customer_id == customer_id
    ).first()

    if not meeting:
        return {"status": "failed", "error": "Meeting not found."}

    try:
        new_start = datetime.fromisoformat(new_slot["start"].replace("Z", "+00:00"))
        new_end = datetime.fromisoformat(new_slot["end"].replace("Z", "+00:00"))
    except Exception as e:
        return {"status": "failed", "error": f"Invalid slot: {e}"}

    if new_start < datetime.now(timezone.utc):
        return {"status": "failed", "error": "Cannot reschedule to a past time."}

    if meeting.google_event_id:
        await _call_mcp_tool("reschedule_calendar_event", {
            "google_event_id": meeting.google_event_id,
            "new_start_iso": new_start.isoformat(),
            "new_end_iso": new_end.isoformat(),
        })

    meeting.scheduled_start = new_start
    meeting.scheduled_end = new_end
    meeting.status = "rescheduled"

    support_user = db.query(SupportUser).filter(SupportUser.id == meeting.support_user_id).first()
    _notify(
        db, customer_id,
        subject="Meeting Rescheduled",
        message=(
            f"Your meeting '{meeting.subject}' has been rescheduled.\n"
            f"New Date: {new_start.strftime('%d %b %Y at %I:%M %p')}\n"
            f"Representative: {support_user.name if support_user else 'Support Team'}"
        ),
        notification_type="meeting_rescheduled",
    )
    db.commit()
    db.refresh(meeting)
    return {
        "status": "rescheduled",
        "meeting_id": meeting_id,
        "scheduled_start": new_start.isoformat(),
        "scheduled_end": new_end.isoformat(),
    }


# ── Shared helpers ────────────────────────────────────────────────────────────

async def _call_mcp_tool(tool_name: str, args: Dict) -> Dict:
    """Find and invoke a named MCP tool, return parsed result dict."""
    tools = await get_calendar_tools()
    tool = next((t for t in tools if t.name == tool_name), None)
    if not tool:
        logger.warning(f"MCP tool '{tool_name}' not found")
        return {}
    try:
        raw = await tool.ainvoke(args)
        if isinstance(raw, str):
            return json.loads(raw)
        return raw if isinstance(raw, dict) else {}
    except Exception as e:
        logger.warning(f"MCP tool '{tool_name}' failed: {e}")
        return {}


def _notify(db: Session, customer_id: int, subject: str, message: str, notification_type: str):
    db.add(Notification(
        customer_id=customer_id,
        channel="in_app",
        subject=subject,
        message=message,
        status="sent",
        notification_type=notification_type,
        is_read=False,
    ))
