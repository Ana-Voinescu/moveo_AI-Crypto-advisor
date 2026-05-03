from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import VoteRequest
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.content_vote import ContentVote

router = APIRouter(prefix="/api", tags=["votes"])


@router.post("/vote")
def submit_vote(
    data: VoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(ContentVote).filter_by(
        user_id=current_user.id,
        content_type=data.content_type,
        content_id=data.content_id,
    ).first()

    if existing:
        existing.vote = data.vote
        existing.updated_at = datetime.now(timezone.utc)
    else:
        db.add(ContentVote(
            user_id=current_user.id,
            content_type=data.content_type,
            content_id=data.content_id,
            vote=data.vote,
        ))

    db.commit()
    return {"success": True}
