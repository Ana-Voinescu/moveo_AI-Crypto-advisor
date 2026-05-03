from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    crypto_assets = Column(JSON, nullable=False)   # e.g. ["BTC", "ETH", "SOL"]
    investor_type = Column(String(50), nullable=False)  # e.g. "hodler"
    content_types = Column(JSON, nullable=False)   # e.g. ["news", "fun"]
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="preferences")
