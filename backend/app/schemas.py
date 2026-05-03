from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional


# --- Auth ---

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_onboarded: bool

    model_config = {"from_attributes": True}

class AuthResponse(BaseModel):
    token: str
    user: UserResponse


# --- Onboarding ---

class OnboardingRequest(BaseModel):
    crypto_assets: List[str]
    investor_type: str
    content_types: List[str]


# --- Dashboard ---

class CoinPrice(BaseModel):
    symbol: str
    price_usd: float
    change_24h: Optional[float] = None

class NewsItem(BaseModel):
    id: str
    title: str
    url: str
    source: str

class MemeItem(BaseModel):
    id: str
    title: str
    url: str

class DashboardResponse(BaseModel):
    prices: List[CoinPrice]
    news: List[NewsItem]
    ai_insight: str
    meme: MemeItem
    votes: dict = {}  # "{content_type}:{content_id}" -> bool


# --- Votes ---

class VoteRequest(BaseModel):
    content_type: str
    content_id: str
    vote: bool
