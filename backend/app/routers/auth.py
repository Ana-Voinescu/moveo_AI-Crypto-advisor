from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import SignupRequest, LoginRequest, AuthResponse
from app.dependencies import get_db
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    user = auth_service.create_user(db, data.name, data.email, data.password)
    token = auth_service.create_token(user.id)
    return {"token": token, "user": user}


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, data.email, data.password)
    token = auth_service.create_token(user.id)
    return {"token": token, "user": user}
