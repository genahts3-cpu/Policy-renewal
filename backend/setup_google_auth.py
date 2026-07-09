"""
Run this ONCE after placing credentials.json in the backend folder.
It opens a browser for Google OAuth consent and saves token.json.

Usage:
    cd backend
    python setup_google_auth.py
"""
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDS_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "token.json")


def main():
    if not os.path.exists(CREDS_FILE):
        print(f"ERROR: '{CREDS_FILE}' not found.")
        print("Download it from Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDs")
        return

    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import httplib2

    # Patch requests to skip SSL verification (corporate proxy)
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import urllib3
    urllib3.disable_warnings()

    class NoSSLAdapter(HTTPAdapter):
        def send(self, *args, **kwargs):
            kwargs["verify"] = False
            return super().send(*args, **kwargs)

    # Monkeypatch requests.Session to always mount NoSSLAdapter
    _orig_session_init = requests.Session.__init__
    def _patched_session_init(self, *args, **kwargs):
        _orig_session_init(self, *args, **kwargs)
        self.mount("https://", NoSSLAdapter())
        self.mount("http://", NoSSLAdapter())
    requests.Session.__init__ = _patched_session_init

    print("Opening browser for Google OAuth consent...")
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"token.json saved. You won't need to do this again unless the token expires.")

    # Quick test
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    service = build("calendar", "v3", credentials=creds, http=http)
    cal = service.calendars().get(calendarId="primary").execute()
    print(f"Connected to calendar: {cal.get('summary')} ({cal.get('id')})")
    print("Google Calendar MCP is ready.")


if __name__ == "__main__":
    main()
