import re
import logging

logger = logging.getLogger(__name__)

OFF_TOPIC_PATTERNS = [
    r"\b(president|prime\s+minister|election|politics|politician)\b",
    r"\b(convert|conversion|exchange\s+rate|rupees?|euros?|pounds?|currency)\b",
    r"\b(weather|forecast|temperature|climate)\b",
    r"\b(recipe|cooking|food|restaurant)\b",
    r"\b(sports?|cricket|football|soccer|basketball|tennis)\b",
    r"\b(movie|film|celebrity|actor|actress|music|song)\b",
    r"\b(stock\s+market|crypto|bitcoin|investment\s+tip)\b",
]

_off_topic_compiled = [re.compile(p, re.IGNORECASE) for p in OFF_TOPIC_PATTERNS]


def check_off_topic(text: str) -> dict:
    for pattern in _off_topic_compiled:
        if pattern.search(text):
            logger.warning(f"Off-topic message detected: {text[:100]}")
            return {"safe": False, "reason": "off_topic"}
    return {"safe": True, "reason": ""}


INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+instructions?",
    r"show\s+(system\s+prompt|database|embeddings|memory|context|secrets?)",
    r"reveal\s+(secrets?|prompt|instructions?|context)",
    r"bypass\s+instructions?",
    r"forget\s+instructions?",
    r"print\s+(memory|context|embeddings?)",
    r"dump\s+(context|database|embeddings?|memory)",
    r"delete\s+database",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"jailbreak",
    r"disregard\s+(all|previous|prior)",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def check_prompt_injection(text: str) -> dict:
    for pattern in _compiled:
        if pattern.search(text):
            logger.warning(f"Prompt injection detected: {text[:100]}")
            return {"safe": False, "reason": "Potential prompt injection detected."}
    return {"safe": True, "reason": ""}
