from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ContentVote(Base):
    __tablename__ = "content_votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_type = Column(String(20), nullable=False)   # "news", "price", "ai_insight", "meme"
    content_id = Column(String(255), nullable=False)
    vote = Column(Boolean, nullable=False)              # True = thumbs up, False = thumbs down
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "content_type", "content_id", name="uq_user_content_vote"),
    )

    user = relationship("User", backref="votes")
