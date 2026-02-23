import random
import httpx
from faker import Faker

fake = Faker()

SOURCES = ["facebook", "google", "form", "email"]
MESSAGES = [
    "Interested in enterprise plan",
    "Need a pricing quote",
    "Just browsing your services",
    "Looking for a demo",
    "Want to discuss trial options",
    "Urgent requirement for our team",
    "Need budget-friendly options",
    "Enterprise level inquiry",
]

def build_payload(source: str) -> dict:
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "message": random.choice(MESSAGES),
        "country": fake.country_code(),
        "source": source,
    }

def fire_fake_lead(base_url: str, token: str):
    source = random.choice(SOURCES)
    payload = build_payload(source)
    is_dupe = random.random() < 0.2
    if is_dupe:
        payload["email"] = "duplicate@example.com"
        payload["phone"] = "0000000000"
    try:
        httpx.post(
            f"{base_url}/webhook/{source}",
            json=payload,
            headers={"X-Secret-Token": token},
            timeout=10,
        )
    except Exception:
        pass