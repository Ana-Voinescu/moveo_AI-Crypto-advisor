from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import OnboardingRequest
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.preferences import UserPreferences

router = APIRouter(prefix="/api", tags=["onboarding"])


@router.post("/onboarding")
def save_onboarding(
    data: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(UserPreferences).filter_by(user_id=current_user.id).first()
    if existing:
        existing.crypto_assets = data.crypto_assets
        existing.investor_type = data.investor_type
        existing.content_types = data.content_types
    else:
        db.add(UserPreferences(
            user_id=current_user.id,
            crypto_assets=data.crypto_assets,
            investor_type=data.investor_type,
            content_types=data.content_types,
        ))

    current_user.is_onboarded = True
    db.commit()
    return {"success": True}
