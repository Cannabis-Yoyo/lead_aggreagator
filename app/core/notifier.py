import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from app.config import settings
from app.models.lead import Lead
from app.models.team import Team


def get_team_email(db: Session, team_name: str) -> str:
    team = db.query(Team).filter(Team.name == team_name).first()
    return team.email if team else settings.NOTIFICATION_EMAIL


def send_lead_notification(db: Session, lead: Lead):
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return
    recipient = get_team_email(db, lead.assigned_team)
    if not recipient or not recipient.strip():
        recipient = settings.NOTIFICATION_EMAIL
    if not recipient:
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"New Lead: {lead.name} via {lead.source}"
    msg["From"] = settings.SMTP_USER
    msg["To"] = recipient
    html = f"""
    <html><body style="font-family:sans-serif;background:#0f172a;color:#f1f5f9;padding:24px;">
    <div style="max-width:520px;margin:auto;background:#1e293b;border-radius:12px;padding:24px;">
        <h2 style="color:#6366f1;margin-top:0;">New Lead Received</h2>
        <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:8px 0;color:#94a3b8;width:40%;">Name</td><td>{lead.name}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Email</td><td>{lead.email}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Phone</td><td>{lead.phone}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Source</td><td>{lead.source}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Country</td><td>{lead.country}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Team</td><td>{lead.assigned_team}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Tags</td><td>{lead.tags}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Message</td><td>{lead.message}</td></tr>
        </table>
    </div></body></html>
    """
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP("smtp.gmail.com", settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, recipient, msg.as_string())