from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models.lead import Lead

router = APIRouter()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Lead).filter(Lead.is_duplicate == False).count()
    today = db.query(Lead).filter(
        Lead.is_duplicate == False,
        func.date(Lead.created_at) == date.today()
    ).count()
    duplicates = db.query(Lead).filter(Lead.is_duplicate == True).count()
    converted = db.query(Lead).filter(Lead.status == "converted").count()

    source_rows = db.query(Lead.source, func.count(Lead.id)).filter(
        Lead.is_duplicate == False
    ).group_by(Lead.source).all()
    sources = {row[0]: row[1] for row in source_rows}

    last_14 = [(date.today() - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    daily_rows = db.query(
        func.date(Lead.created_at).label("day"),
        func.count(Lead.id).label("count")
    ).filter(Lead.is_duplicate == False).group_by("day").all()
    daily_map = {str(r.day): r.count for r in daily_rows}
    leads_over_time = [{"date": d, "count": daily_map.get(d, 0)} for d in last_14]

    return {
        "total_leads": total,
        "today_leads": today,
        "duplicate_count": duplicates,
        "conversion_count": converted,
        "sources": sources,
        "leads_over_time": leads_over_time,
    }