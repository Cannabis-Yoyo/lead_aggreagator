import hashlib
import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.config import settings

def normalize_email(email: str) -> str:
    return email.strip().lower() if email else ""

def normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone) if phone else ""

def generate_fingerprint(email: str, phone: str) -> str:
    key = normalize_email(email) + normalize_phone(phone)
    return hashlib.sha256(key.encode()).hexdigest()

def is_duplicate(db: Session, fingerprint: str) -> bool:
    expiry = datetime.utcnow() - timedelta(days=settings.LEAD_EXPIRY_DAYS)
    return db.query(Lead).filter(
        Lead.fingerprint == fingerprint,
        Lead.created_at >= expiry
    ).first() is not None