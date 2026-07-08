import time
from collections import defaultdict
from fastapi import HTTPException

# {user_id: [timestamps]}
_request_log: dict = defaultdict(list)
WINDOW_SECONDS = 60
MAX_REQUESTS = 5


def check_rate_limit(user_id: int):
    now = time.time()
    window_start = now - WINDOW_SECONDS
    timestamps = _request_log[user_id]
    # Remove old entries
    _request_log[user_id] = [t for t in timestamps if t > window_start]
    if len(_request_log[user_id]) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {MAX_REQUESTS} requests per minute.",
        )
    _request_log[user_id].append(now)
