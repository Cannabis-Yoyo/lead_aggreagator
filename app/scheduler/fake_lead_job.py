from apscheduler.schedulers.background import BackgroundScheduler
from app.simulator.lead_generator import fire_fake_lead
from app.config import settings

scheduler = BackgroundScheduler()

def start_scheduler(base_url: str):
    scheduler.add_job(
        fire_fake_lead,
        "interval",
        minutes=settings.SCHEDULER_INTERVAL_MINUTES,
        args=[base_url, settings.SECRET_TOKEN],
        id="fake_lead_job",
        replace_existing=True,
    )
    scheduler.start()

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()