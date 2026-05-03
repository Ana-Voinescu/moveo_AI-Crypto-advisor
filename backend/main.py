from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, onboarding, dashboard, votes
from app.config import FRONTEND_URL

app = FastAPI(title="Crypto Advisor API", version="1.0.0")

_origins = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]
if FRONTEND_URL:
    _origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(dashboard.router)
app.include_router(votes.router)


@app.get("/health")
def health():
    return {"status": "ok"}
