import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY must be set")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

FRONTEND_URL = os.getenv("FRONTEND_URL", "")
