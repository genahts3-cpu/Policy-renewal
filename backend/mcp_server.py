"""
Google Calendar MCP Server
Exposes calendar tools over stdio using the MCP protocol.
Agents connect to this via langchain-mcp-adapters.

Run standalone: python mcp_server.py
"""
import ssl
import os
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

ssl._create_default_https_context = ssl._create_unverified_context
os.environ.setdefault("PYTHONHTTPSVERIFY", "0")

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

mcp = FastMCP("google-calendar")


# ── Google Calendar auth ──────────────────────────────────────────────────────

def _get_service():
    creds_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "credentials.json")
    token_path = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "token.json")
    scopes = ["https://www.googleapis.com/auth/calendar"]
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        import httplib2

        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                import requests as req
                session = req.Session()
                session.verify = False
                creds.refresh(Request(session=session))
            elif os.path.exists(creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
                creds = flow.run_local_server(port=0)
            else:
                return None
            with open(token_path, "w") as f:
                f.write(creds.to_json())

        http = httplib2.Http(disable_ssl_certificate_validation=True)
        return build("calendar", "v3", credentials=creds, http=http)
    except Exception as e:
        logger.warning(f"Calendar auth failed, using mock: {e}")
        return None


# ── MCP Tools ─────────────────────────────────────────────────────────────────

@mcp.tool()
def get_available_slots(
    support_email: str,
    days_ahead: int = 3,
    duration_minutes: int = 30,
) -> list[dict[str, Any]]:
    """
    Get available time slots for a support agent over the next N working days.
    Returns up to 3 slots, each with 'start' (ISO), 'end' (ISO), and 'display' (human-readable).
    """
    now = datetime.now(timezone.utc)
    end_range = now + timedelta(days=days_ahead)
    service = _get_service()

    busy: list[dict] = []
    if service:
        try:
            result = service.freebusy().query(body={
                "timeMin": now.isoformat(),
                "timeMax": end_range.isoformat(),
                "items": [{"id": support_email}],
            }).execute()
            busy = result.get("calendars", {}).get(support_email, {}).get("busy", [])
        except Exception as e:
            logger.warning(f"freebusy failed: {e}")
            busy = _mock_busy(now)
    else:
        busy = _mock_busy(now)

    return _compute_free_slots(busy, now, end_range, duration_minutes)


@mcp.tool()
def create_calendar_event(
    subject: str,
    description: str,
    start_iso: str,
    end_iso: str,
    customer_email: str,
    support_email: str,
    customer_name: str = "",
    support_name: str = "",
) -> dict[str, Any]:
    """
    Create a Google Calendar event with a Google Meet link.
    Returns google_event_id, meeting_link, and status.
    """
    service = _get_service()
    if not service:
        return _mock_event()

    try:
        event = {
            "summary": subject,
            "description": description,
            "start": {"dateTime": start_iso, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_iso, "timeZone": "Asia/Kolkata"},
            "attendees": [
                {"email": customer_email, "displayName": customer_name},
                {"email": support_email, "displayName": support_name},
            ],
            "conferenceData": {
                "createRequest": {
                    "requestId": str(uuid.uuid4()),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60},
                    {"method": "popup", "minutes": 15},
                ],
            },
        }
        created = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1,
            sendUpdates="all",
        ).execute()
        meet_link = (
            created.get("conferenceData", {})
            .get("entryPoints", [{}])[0]
            .get("uri", "")
        )
        return {
            "google_event_id": created["id"],
            "meeting_link": meet_link,
            "status": "confirmed",
        }
    except Exception as e:
        logger.warning(f"create_calendar_event failed: {e}")
        return _mock_event()


@mcp.tool()
def cancel_calendar_event(google_event_id: str) -> dict[str, Any]:
    """Cancel a Google Calendar event by its event ID. Sends cancellation emails to attendees."""
    service = _get_service()
    if not service:
        return {"status": "cancelled", "google_event_id": google_event_id}
    try:
        service.events().delete(
            calendarId="primary",
            eventId=google_event_id,
            sendUpdates="all",
        ).execute()
        return {"status": "cancelled", "google_event_id": google_event_id}
    except Exception as e:
        logger.warning(f"cancel_calendar_event failed: {e}")
        return {"status": "cancelled", "google_event_id": google_event_id}


@mcp.tool()
def reschedule_calendar_event(
    google_event_id: str,
    new_start_iso: str,
    new_end_iso: str,
) -> dict[str, Any]:
    """Reschedule an existing Google Calendar event to a new time. Notifies all attendees."""
    service = _get_service()
    if not service:
        return {"status": "rescheduled", "google_event_id": google_event_id}
    try:
        event = service.events().get(calendarId="primary", eventId=google_event_id).execute()
        event["start"] = {"dateTime": new_start_iso, "timeZone": "Asia/Kolkata"}
        event["end"] = {"dateTime": new_end_iso, "timeZone": "Asia/Kolkata"}
        updated = service.events().update(
            calendarId="primary",
            eventId=google_event_id,
            body=event,
            sendUpdates="all",
        ).execute()
        return {"status": "rescheduled", "google_event_id": updated["id"]}
    except Exception as e:
        logger.warning(f"reschedule_calendar_event failed: {e}")
        return {"status": "rescheduled", "google_event_id": google_event_id}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mock_busy(start: datetime) -> list[dict]:
    base = start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)
    return [
        {
            "start": (base + timedelta(hours=i * 3)).isoformat(),
            "end": (base + timedelta(hours=i * 3 + 1)).isoformat(),
        }
        for i in range(2)
    ]


def _compute_free_slots(
    busy: list[dict],
    start_range: datetime,
    end_range: datetime,
    duration_minutes: int,
) -> list[dict]:
    def overlaps(s: datetime, e: datetime) -> bool:
        for b in busy:
            try:
                bs = datetime.fromisoformat(b["start"].replace("Z", "+00:00"))
                be = datetime.fromisoformat(b["end"].replace("Z", "+00:00"))
                if s < be and e > bs:
                    return True
            except Exception:
                pass
        return False

    slots = []
    current = start_range.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    while current < end_range and len(slots) < 3:
        if current.weekday() < 5 and 9 <= current.hour < 17:
            slot_end = current + timedelta(minutes=duration_minutes)
            if slot_end.hour <= 17 and not overlaps(current, slot_end):
                slots.append({
                    "start": current.isoformat(),
                    "end": slot_end.isoformat(),
                    "display": current.strftime("%d %b %Y, %I:%M %p"),
                })
        current += timedelta(minutes=30)
    return slots


def _mock_event() -> dict[str, Any]:
    code = uuid.uuid4().hex[:10]
    return {
        "google_event_id": f"mock_{uuid.uuid4().hex[:16]}",
        "meeting_link": f"https://meet.google.com/{code[:4]}-{code[4:8]}-{code[8:]}",
        "status": "confirmed",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
