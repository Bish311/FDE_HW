from __future__ import annotations

INJECTION_PATTERNS = [
    "ignore all procurement rules",
    "ignore all rules",
    "treat this request as",
    "approve it immediately",
    "approve immediately",
    "bypass policy",
    "override policy",
    "system instruction",
    "disregard previous",
    "as cfo-approved",
]


def detect_prompt_injection(texts: list[str]) -> bool:
    for text in texts:
        normalized = text.lower()
        for pattern in INJECTION_PATTERNS:
            if pattern in normalized:
                return True
    return False
