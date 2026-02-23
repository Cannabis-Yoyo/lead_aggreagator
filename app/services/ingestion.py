from app.schemas.lead import WebhookPayload

SOURCE_FIELD_MAP = {
    "facebook": {"full_name": "name", "email_address": "email", "phone_number": "phone", "country_code": "country"},
    "google": {"FULL_NAME": "name", "EMAIL": "email", "PHONE_NUMBER": "phone", "COUNTRY": "country"},
}

def normalize_payload(source: str, raw: dict) -> WebhookPayload:
    field_map = SOURCE_FIELD_MAP.get(source, {})
    normalized = {}
    for raw_key, value in raw.items():
        standard_key = field_map.get(raw_key, raw_key)
        normalized[standard_key] = value
    normalized["source"] = source
    valid_fields = WebhookPayload.model_fields.keys()
    return WebhookPayload(**{k: v for k, v in normalized.items() if k in valid_fields})