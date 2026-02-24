import os
from flask import Flask, request, jsonify, render_template, redirect
from dotenv import load_dotenv

load_dotenv()

from app.database import create_tables, SessionLocal
from app.core.routing import seed_default_rules, seed_default_teams
from app.models.lead import Lead
from app.models.routing_rule import RoutingRule
from app.services.ingestion import normalize_payload
from app.core.deduplication import generate_fingerprint, is_duplicate
from app.core.tagging import apply_tags, tags_to_str
from app.core.routing import evaluate_rules
from app.core.notifier import send_lead_notification
from app.config import settings
from sqlalchemy import desc, func
from datetime import date, timedelta

app = Flask(__name__, template_folder='templates', static_folder='../static')

create_tables()
_db = SessionLocal()
seed_default_teams(_db)
seed_default_rules(_db)
_db.close()


def get_db():
    return SessionLocal()


def build_stats(db):
    total = db.query(Lead).filter(Lead.is_duplicate == False).count()
    today = db.query(Lead).filter(
        Lead.is_duplicate == False,
        func.date(Lead.created_at) == date.today()
    ).count()
    duplicates = db.query(Lead).filter(Lead.is_duplicate == True).count()
    converted = db.query(Lead).filter(Lead.status == 'converted').count()
    source_rows = db.query(Lead.source, func.count(Lead.id)).filter(
        Lead.is_duplicate == False
    ).group_by(Lead.source).all()
    sources = {row[0]: row[1] for row in source_rows}
    last_14 = [(date.today() - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    daily_rows = db.query(
        func.date(Lead.created_at).label('day'),
        func.count(Lead.id).label('count')
    ).filter(Lead.is_duplicate == False).group_by('day').all()
    daily_map = {str(r.day): r.count for r in daily_rows}
    leads_over_time = [{'date': d, 'count': daily_map.get(d, 0)} for d in last_14]
    return {
        'total_leads': total,
        'today_leads': today,
        'duplicate_count': duplicates,
        'conversion_count': converted,
        'sources': sources,
        'leads_over_time': leads_over_time,
    }


@app.route('/')
def index():
    db = get_db()
    stats = build_stats(db)
    recent = db.query(Lead).filter(Lead.is_duplicate == False).order_by(desc(Lead.created_at)).limit(8).all()
    db.close()
    return render_template('dashboard.html', stats=stats, recent=recent)


@app.route('/leads-page')
def leads_page():
    db = get_db()
    all_leads = db.query(Lead).filter(Lead.is_duplicate == False).order_by(desc(Lead.created_at)).limit(200).all()
    db.close()
    return render_template('leads.html', leads=all_leads)


@app.route('/lead/<int:lead_id>')
def lead_detail(lead_id):
    db = get_db()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    db.close()
    return render_template('lead_detail.html', lead=lead)


@app.route('/routing-page')
def routing_page():
    db = get_db()
    rules = db.query(RoutingRule).order_by(RoutingRule.priority).all()
    db.close()
    return render_template('routing_rules.html', rules=rules)


@app.route('/webhook/<source>', methods=['POST'])
def ingest_lead(source):
    token = request.headers.get('X-Secret-Token', '')
    if token != settings.SECRET_TOKEN:
        return jsonify({'error': 'Invalid token'}), 403
    raw = request.get_json()
    payload = normalize_payload(source, raw)
    fingerprint = generate_fingerprint(payload.email or '', payload.phone or '')
    db = get_db()
    duplicate = is_duplicate(db, fingerprint)
    tags = apply_tags(source, payload.message, payload.country, payload.phone)
    assigned_team = evaluate_rules(db, source, payload.message, payload.country, tags)
    if duplicate:
        db.close()
        return jsonify({'status': 'duplicate', 'action': 'skipped'})
    lead = Lead(
        fingerprint=fingerprint,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        source=source,
        message=payload.message,
        country=payload.country,
        tags=tags_to_str(tags),
        assigned_team=assigned_team,
        status='new',
        is_duplicate=False,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    send_lead_notification(db, lead)
    db.close()
    return jsonify({'status': 'accepted', 'lead_id': lead.id, 'team': assigned_team})


@app.route('/leads/<int:lead_id>/status', methods=['POST'])
def update_status(lead_id):
    db = get_db()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        db.close()
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json()
    lead.status = data.get('status', lead.status)
    db.commit()
    db.close()
    return jsonify({'status': 'updated'})


@app.route('/trigger-lead', methods=['POST'])
def trigger_lead():
    import threading
    def fire():
        from app.simulator.lead_generator import fire_fake_lead
        fire_fake_lead(
            base_url='https://workapp.pythonanywhere.com',
            token=settings.SECRET_TOKEN
        )
    threading.Thread(target=fire).start()
    return redirect('/')


@app.route('/stats')
def stats():
    db = get_db()
    result = build_stats(db)
    db.close()
    return jsonify(result)