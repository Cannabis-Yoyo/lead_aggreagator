from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadOut, LeadStatusUpdate

router = APIRouter()

@router.get("/leads", response_model=list[LeadOut])
def list_leads(
    db: Session = Depends(get_db),
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    team: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
):
    q = db.query(Lead).filter(Lead.is_duplicate == False)
    if source:
        q = q.filter(Lead.source == source)
    if status:
        q = q.filter(Lead.status == status)
    if team:
        q = q.filter(Lead.assigned_team == team)
    return q.order_by(desc(Lead.created_at)).offset(skip).limit(limit).all()

@router.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/leads/{lead_id}/status")
def update_status(lead_id: int, body: LeadStatusUpdate, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = body.status
    db.commit()
    return {"status": "updated"}