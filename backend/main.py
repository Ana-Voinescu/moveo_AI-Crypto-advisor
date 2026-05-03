from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, onboarding, dashboard, votes

app = FastAPI(title="Crypto Advisor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
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
