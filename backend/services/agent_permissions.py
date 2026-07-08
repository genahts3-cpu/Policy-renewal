from fastapi import HTTPException

AGENT_PERMISSIONS = {
    "QAAgent": {
        "can": ["read_chromadb"],
        "cannot": ["renew_policy", "update_database"],
    },
    "RenewalAgent": {
        "can": ["renew_policy"],
        "cannot": ["read_other_customers"],
    },
    "NotificationAgent": {
        "can": ["send_notifications"],
        "cannot": ["access_embeddings"],
    },
    "GoalAgent": {
        "can": ["read_message", "classify_intent"],
        "cannot": ["renew_policy", "update_database"],
    },
    "MemoryAgent": {
        "can": ["read_customer_data", "write_conversation"],
        "cannot": ["read_other_customers"],
    },
}


def enforce_permission(agent_name: str, action: str):
    perms = AGENT_PERMISSIONS.get(agent_name)
    if not perms:
        return
    if action in perms["cannot"]:
        raise HTTPException(
            status_code=403,
            detail=f"Agent '{agent_name}' is not permitted to perform '{action}'.",
        )
