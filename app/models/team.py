from sqlalchemy import Column, Integer, String
from app.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)
    email = Column(String(120))