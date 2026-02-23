import sys
sys.path.append(".")

from faker import Faker
from datetime import datetime, timedelta
import random, json, hashlib, re

fake = Faker()

from app.database import SessionLocal, create_tables
from app.models.lead import Lead

SOURCES = ["facebook", "google", "form", "email"]
MESSAGES = [
    "Interested in enterprise plan", "Need a pricing quote",
    "Looking for a demo", "Want to discuss trial options",
    "Urgent requirement", "Need budget-friendly options",
    "Just browsing", "Enterprise level inquiry",
]
TEAMS = ["digital-team", "sales-team", "support-team", "inbound-team", "general-team"]
STATUSES = ["new", "new", "new", "contacted", "converted", "junk"]

def fingerprint(email, phone):
    phone = re.sub(r"\D", "", phone) if phone else ""
    return hashlib.sha256((email.lower() + phone).encode()).hexdigest()

create_tables()
db = SessionLocal()

for i in range(200):
    source = random.choice(SOURCES)
    email = fake.email()
    phone = fake.phone_number()
    fp = fingerprint(email, phone)
    days_ago = random.randint(0, 30)
    created = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
    tags = json.dumps([f"source:{source}", random.choice(["high-value", "demo-request", "incomplete", "urgent"])])

    if db.query(Lead).filter(Lead.fingerprint == fp).first():
        continue

    lead = Lead(
        fingerprint=fp,
        name=fake.name(),
        email=email,
        phone=phone,
        source=source,
        message=random.choice(MESSAGES),
        country=fake.country_code(),
        tags=tags,
        assigned_team=random.choice(TEAMS),
        status=random.choice(STATUSES),
        is_duplicate=False,
        created_at=created,
    )
    db.add(lead)

db.commit()
db.close()
print("Seeded 200 leads.")