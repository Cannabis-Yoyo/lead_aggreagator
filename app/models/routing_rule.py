from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class RoutingRule(Base):
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(30))
    keyword = Column(String(120))
    country = Column(String(10))
    tag = Column(String(80))
    assign_to_team = Column(String(80))
    priority = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)