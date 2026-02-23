from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import create_tables, get_db
from app.config import settings
from app.core.routing import seed_default_rules, seed_default_teams
from app.scheduler.fake_lead_job import start_scheduler, stop_scheduler
from app.api import webhooks, leads, dashboard
from app.models.lead import Lead
from app.models.routing_rule import RoutingRule
from sqlalchemy import desc

templates = Jinja2Templates(directory="app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    db = next(get_db())
    seed_default_teams(db)
    seed_default_rules(db)
    db.close()
    start_scheduler(base_url="https://workapp.pythonanywhere.com")
    yield
    stop_scheduler()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(webhooks.router, tags=["Webhooks"])
app.include_router(leads.router, tags=["Leads"])
app.include_router(dashboard.router, tags=["Dashboard"])


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    from app.api.dashboard import get_stats
    stats = get_stats(db)
    recent = db.query(Lead).filter(Lead.is_duplicate == False).order_by(desc(Lead.created_at)).limit(8).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent": recent,
    })

@app.get("/leads-page")
def leads_page(request: Request, db: Session = Depends(get_db)):
    all_leads = db.query(Lead).filter(Lead.is_duplicate == False).order_by(desc(Lead.created_at)).limit(200).all()
    return templates.TemplateResponse("leads.html", {"request": request, "leads": all_leads})

@app.get("/lead/{lead_id}")
def lead_detail(lead_id: int, request: Request, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    return templates.TemplateResponse("lead_detail.html", {"request": request, "lead": lead})

@app.get("/routing-page")
def routing_page(request: Request, db: Session = Depends(get_db)):
    rules = db.query(RoutingRule).order_by(RoutingRule.priority).all()
    return templates.TemplateResponse("routing_rules.html", {"request": request, "rules": rules})

@app.post("/trigger-lead")
def trigger_lead(db: Session = Depends(get_db)):
    from app.simulator.lead_generator import fire_fake_lead
    fire_fake_lead(base_url="http://127.0.0.1:8000", token=settings.SECRET_TOKEN)
    return {"status": "triggered"}