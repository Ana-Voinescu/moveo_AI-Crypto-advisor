from pydantic import BaseModel, EmailStr
from typing import List, Optional


# --- Auth ---

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

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


# --- Votes ---

class VoteRequest(BaseModel):
    content_type: str
    content_id: str
    vote: bool
