import re


def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}"


def mask_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return phone
    return digits[:3] + "*" * (len(digits) - 5) + digits[-2:]


def mask_policy_number(policy_number: str) -> str:
    if not policy_number or len(policy_number) < 6:
        return policy_number
    return policy_number[:3] + "*" * (len(policy_number) - 6) + policy_number[-3:]


def mask_address(address: str) -> str:
    if not address:
        return address
    parts = address.split(",")
    parts[0] = "***"
    return ",".join(parts)


def mask_pii(text: str) -> str:
    # Mask emails
    text = re.sub(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
        lambda m: mask_email(m.group()),
        text,
    )
    # Mask phone numbers (10+ digit sequences)
    text = re.sub(
        r"\b(\+?\d[\d\s\-]{8,}\d)\b",
        lambda m: mask_phone(m.group()),
        text,
    )
    # Mask policy numbers like POL-XXXXX
    text = re.sub(
        r"\bPOL-\d{5}\b",
        lambda m: mask_policy_number(m.group()),
        text,
    )
    return text
