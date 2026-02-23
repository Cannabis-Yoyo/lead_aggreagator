from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    fingerprint = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(120))
    email = Column(String(120), index=True)
    phone = Column(String(30))
    source = Column(String(30), index=True)
    message = Column(Text)
    country = Column(String(10))
    tags = Column(Text, default="[]")
    assigned_team = Column(String(80))
    status = Column(String(20), default="new", index=True)
    is_duplicate = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())