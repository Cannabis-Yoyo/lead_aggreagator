from sqlalchemy.orm import Session
from app.models.routing_rule import RoutingRule
from typing import Optional, List


def evaluate_rules(db: Session, source: str, message: str, country: str, tags: List[str]) -> Optional[str]:
    rules = (
        db.query(RoutingRule)
        .filter(RoutingRule.is_active == True)
        .order_by(RoutingRule.priority.asc())
        .all()
    )
    message_lower = (message or "").lower()
    for rule in rules:
        source_match = not rule.source or rule.source == source
        keyword_match = not rule.keyword or rule.keyword.lower() in message_lower
        country_match = not rule.country or rule.country.upper() == (country or "").upper()
        if source_match and keyword_match and country_match:
            return rule.assign_to_team
    return "general-team"


def seed_default_rules(db: Session):
    if db.query(RoutingRule).count() > 0:
        return
    defaults = [
        RoutingRule(source="facebook", assign_to_team="digital-team", priority=1, tag="social"),
        RoutingRule(source="google", assign_to_team="digital-team", priority=2, tag="social"),
        RoutingRule(keyword="enterprise", assign_to_team="sales-team", priority=3, tag="high-value"),
        RoutingRule(keyword="demo", assign_to_team="sales-team", priority=4, tag="demo-request"),
        RoutingRule(source="email", assign_to_team="support-team", priority=5, tag="email-lead"),
        RoutingRule(source="form", assign_to_team="inbound-team", priority=6, tag="form-lead"),
    ]
    db.add_all(defaults)
    db.commit()


def seed_default_teams(db: Session):
    from app.models.team import Team
    if db.query(Team).count() > 0:
        return
    from app.config import settings
    teams = [
        Team(name="digital-team", email=settings.NOTIFICATION_EMAIL),
        Team(name="sales-team", email=settings.NOTIFICATION_EMAIL),
        Team(name="support-team", email=settings.NOTIFICATION_EMAIL),
        Team(name="inbound-team", email=settings.NOTIFICATION_EMAIL),
        Team(name="general-team", email=settings.NOTIFICATION_EMAIL),
    ]
    db.add_all(teams)
    db.commit()