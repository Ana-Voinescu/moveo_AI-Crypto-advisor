# Crypto Investor Dashboard

A personalized crypto dashboard that learns your investment style through a short onboarding quiz and delivers daily AI-curated content tailored to your interests.

**Live app:** https://moveo-ai-crypto-advisor-five.vercel.app  
**API:** https://moveo-ai-crypto-advisor-iyl5.onrender.com

---

## Features

- **Auth** — Register and log in with email and password (JWT-based)
- **Onboarding** — Choose your crypto assets, investor type, and content preferences
- **Daily Dashboard** — Four sections updated on every load:
  - 📈 Coin Prices (CoinGecko API)
  - 📰 Market News (newsdata.io API — crypto category, filtered by selected coins)
  - 🤖 AI Insight of the Day (OpenRouter — Gemma 3 12B)
  - 😂 Crypto Meme (Reddit scraping)
- **Voting** — Thumbs up/down on every section, stored in the database and restored on reload
- **Fallbacks** — All external APIs have static fallback data so the dashboard never crashes

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, React Router, plain CSS |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | SQLite (local) / PostgreSQL (production) |
| Auth | JWT via PyJWT, passwords hashed with bcrypt |
| Deployment | Vercel (frontend), Render (backend + DB) |

---

## Running Locally

### Prerequisites
- Node.js 18+
- Python 3.11+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your API keys
python create_tables.py
uvicorn main:app --reload --port 8000
```

The API will be available at http://localhost:8000.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # set VITE_API_URL=http://localhost:8000
npm run dev
```

The app will be available at http://localhost:5173.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | No | Defaults to `sqlite:///./dev.db` |
| `JWT_SECRET_KEY` | Yes (prod) | Secret key for signing tokens — use a long random string in production |
| `NEWSDATA_API_KEY` | No | Get free key at newsdata.io — falls back to static data without it |
| `OPENROUTER_API_KEY` | No | Get free key at openrouter.ai — falls back to static insight without it |
| `FRONTEND_URL` | No | Production frontend URL added to CORS allowed origins |

> **Note on news provider:** CryptoPanic was the original news source, but as of April 1, 2026 they discontinued their free tier. newsdata.io was chosen as a free alternative — its `/api/1/crypto` endpoint returns crypto-specific news only, and results are filtered further by the user's selected coin symbols (e.g. BTC, ETH).

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | No | Backend URL — defaults to `http://localhost:8000` |

---

## Running Tests

### Backend (40 tests)

```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend (25 tests)

```bash
cd frontend
npm test
```

---

## Project Structure

```
moveo/
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy models (User, UserPreferences, ContentVote)
│   │   ├── routers/        # FastAPI route handlers (auth, onboarding, dashboard, votes)
│   │   ├── services/       # External API integrations with static fallbacks
│   │   ├── config.py       # Environment variable loading
│   │   ├── database.py     # SQLAlchemy engine and session factory
│   │   ├── dependencies.py # Shared FastAPI dependencies (get_db, get_current_user)
│   │   └── schemas.py      # Pydantic request/response models
│   ├── tests/              # pytest test suite
│   ├── create_tables.py    # Database initialisation script
│   └── main.py             # FastAPI app entry point
└── frontend/
    ├── src/
    │   ├── components/     # Auth, dashboard cards, onboarding form, shared components
    │   ├── context/        # AuthContext (global auth state)
    │   ├── pages/          # Page-level components
    │   ├── services/       # api.js — all HTTP calls in one place
    │   └── tests/          # Vitest + Testing Library test suite
    └── vite.config.js
```
