import json
from typing import List

KEYWORD_TAGS = {
    "enterprise": "high-value",
    "urgent": "urgent",
    "budget": "budget-conscious",
    "demo": "demo-request",
    "pricing": "pricing-inquiry",
    "trial": "trial-request",
}

def apply_tags(source: str, message: str, country: str, phone: str) -> List[str]:
    tags = []
    if source:
        tags.append(f"source:{source}")
    if not phone or len(phone) < 6:
        tags.append("incomplete")
    if message:
        msg_lower = message.lower()
        for keyword, tag in KEYWORD_TAGS.items():
            if keyword in msg_lower:
                tags.append(tag)
    if country:
        tags.append(f"country:{country.upper()}")
    return list(set(tags))

def tags_to_str(tags: List[str]) -> str:
    return json.dumps(tags)

def str_to_tags(tags_str: str) -> List[str]:
    try:
        return json.loads(tags_str)
    except Exception:
        return []