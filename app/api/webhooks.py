from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.services.ingestion import normalize_payload
from app.core.deduplication import generate_fingerprint, is_duplicate
from app.core.tagging import apply_tags, tags_to_str
from app.core.routing import evaluate_rules
from app.core.notifier import send_lead_notification
from app.models.lead import Lead

router = APIRouter()

def verify_token(x_secret_token: str = Header(...)):
    if x_secret_token != settings.SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

@router.post("/webhook/{source}")
async def ingest_lead(
    source: str,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    raw = await request.json()
    payload = normalize_payload(source, raw)

    fingerprint = generate_fingerprint(payload.email or "", payload.phone or "")
    duplicate = is_duplicate(db, fingerprint)

    tags = apply_tags(source, payload.message, payload.country, payload.phone)
    assigned_team = evaluate_rules(db, source, payload.message, payload.country, tags)

    lead = Lead(
        fingerprint=fingerprint,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        source=source,
        message=payload.message,
        country=payload.country,
        tags=tags_to_str(tags),
        assigned_team=assigned_team if not duplicate else None,
        status="new",
        is_duplicate=duplicate,
    )

    if duplicate:
        return {"status": "duplicate", "action": "skipped"}

    db.add(lead)
    db.commit()
    db.refresh(lead)
    send_lead_notification(db, lead)
    return {"status": "accepted", "lead_id": lead.id, "team": assigned_team}