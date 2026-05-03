import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import DashboardResponse
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.preferences import UserPreferences
from app.models.content_vote import ContentVote
from app.services import coingecko, cryptopanic, ai_service, meme_service

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prefs = db.query(UserPreferences).filter_by(user_id=current_user.id).first()
    if not prefs:
        raise HTTPException(status_code=400, detail="Please complete onboarding first")

    prices, news, insight, meme = await asyncio.gather(
        coingecko.get_prices(prefs.crypto_assets),
        cryptopanic.get_news(prefs.crypto_assets),
        ai_service.get_insight(prefs),
        meme_service.get_meme(),
    )

    existing_votes = db.query(ContentVote).filter_by(user_id=current_user.id).all()
    votes = {f"{v.content_type}:{v.content_id}": v.vote for v in existing_votes}

    return DashboardResponse(prices=prices, news=news, ai_insight=insight, meme=meme, votes=votes)
