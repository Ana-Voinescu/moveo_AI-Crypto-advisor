"""
API endpoint tests.

Each test gets a fresh in-memory DB via the `client` fixture in conftest.py.
External service calls are mocked so tests never hit real APIs.
"""
from unittest.mock import patch, AsyncMock
from app.schemas import CoinPrice, NewsItem, MemeItem


# --- Shared mock data for dashboard tests ---

_PRICES = [CoinPrice(symbol="BTC", price_usd=60000.0, change_24h=1.0)]
_NEWS = [NewsItem(id="n1", title="Test News", url="http://news.com", source="TestSource")]
_INSIGHT = "Stay calm and HODL."
_MEME = MemeItem(id="m1", title="Moon soon", url="http://i.redd.it/meme.jpg")


# --- Helpers ---

def _signup(client, email="user@test.com", password="testpass123"):
    resp = client.post("/api/auth/signup", json={
        "name": "Test User", "email": email, "password": password,
    })
    return resp.json()["token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _onboard(client, token, assets=None, investor_type="hodler", content_types=None):
    client.post("/api/onboarding", json={
        "crypto_assets": assets or ["BTC"],
        "investor_type": investor_type,
        "content_types": content_types or ["news"],
    }, headers=_auth(token))


def _mock_dashboard():
    """Context manager that patches all four external service calls."""
    return (
        patch("app.routers.dashboard.coingecko.get_prices", AsyncMock(return_value=_PRICES)),
        patch("app.routers.dashboard.cryptopanic.get_news", AsyncMock(return_value=_NEWS)),
        patch("app.routers.dashboard.ai_service.get_insight", AsyncMock(return_value=_INSIGHT)),
        patch("app.routers.dashboard.meme_service.get_meme", AsyncMock(return_value=_MEME)),
    )


# ============================================================
# Signup
# ============================================================

def test_signup_returns_token_and_user(client):
    resp = client.post("/api/auth/signup", json={
        "name": "Anna", "email": "anna@test.com", "password": "secret123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["user"]["name"] == "Anna"
    assert data["user"]["email"] == "anna@test.com"
    assert data["user"]["is_onboarded"] is False


def test_signup_duplicate_email_returns_400(client):
    payload = {"name": "Anna", "email": "anna@test.com", "password": "secret123"}
    client.post("/api/auth/signup", json=payload)
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


# ============================================================
# Login
# ============================================================

def test_login_returns_token(client):
    _signup(client)
    resp = client.post("/api/auth/login", json={
        "email": "user@test.com", "password": "testpass123",
    })
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_login_wrong_password_returns_401(client):
    _signup(client)
    resp = client.post("/api/auth/login", json={
        "email": "user@test.com", "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_login_unknown_email_returns_401(client):
    resp = client.post("/api/auth/login", json={
        "email": "nobody@test.com", "password": "pass",
    })
    assert resp.status_code == 401


# ============================================================
# Onboarding
# ============================================================

def test_onboarding_saves_and_returns_success(client):
    token = _signup(client)
    resp = client.post("/api/onboarding", json={
        "crypto_assets": ["BTC", "ETH"],
        "investor_type": "hodler",
        "content_types": ["news", "fun"],
    }, headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_onboarding_without_token_returns_403(client):
    resp = client.post("/api/onboarding", json={
        "crypto_assets": ["BTC"], "investor_type": "hodler", "content_types": ["news"],
    })
    assert resp.status_code == 403


def test_onboarding_can_be_updated(client):
    token = _signup(client)
    _onboard(client, token, assets=["BTC"], investor_type="hodler")
    # Update to different preferences — should not fail or create a duplicate row
    resp = client.post("/api/onboarding", json={
        "crypto_assets": ["SOL", "ADA"],
        "investor_type": "day_trader",
        "content_types": ["charts"],
    }, headers=_auth(token))
    assert resp.status_code == 200


# ============================================================
# Dashboard
# ============================================================

def test_dashboard_returns_all_four_sections(client):
    token = _signup(client)
    _onboard(client, token)

    with patch("app.routers.dashboard.coingecko.get_prices", AsyncMock(return_value=_PRICES)), \
         patch("app.routers.dashboard.cryptopanic.get_news", AsyncMock(return_value=_NEWS)), \
         patch("app.routers.dashboard.ai_service.get_insight", AsyncMock(return_value=_INSIGHT)), \
         patch("app.routers.dashboard.meme_service.get_meme", AsyncMock(return_value=_MEME)):
        resp = client.get("/api/dashboard", headers=_auth(token))

    assert resp.status_code == 200
    data = resp.json()
    assert data["prices"][0]["symbol"] == "BTC"
    assert data["news"][0]["title"] == "Test News"
    assert data["ai_insight"] == "Stay calm and HODL."
    assert data["meme"]["id"] == "m1"


def test_dashboard_without_token_returns_403(client):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 403


def test_dashboard_before_onboarding_returns_400(client):
    token = _signup(client)  # signed up but not onboarded
    with patch("app.routers.dashboard.coingecko.get_prices", AsyncMock(return_value=_PRICES)), \
         patch("app.routers.dashboard.cryptopanic.get_news", AsyncMock(return_value=_NEWS)), \
         patch("app.routers.dashboard.ai_service.get_insight", AsyncMock(return_value=_INSIGHT)), \
         patch("app.routers.dashboard.meme_service.get_meme", AsyncMock(return_value=_MEME)):
        resp = client.get("/api/dashboard", headers=_auth(token))
    assert resp.status_code == 400


# ============================================================
# Vote
# ============================================================

def test_vote_thumbs_up_returns_success(client):
    token = _signup(client)
    resp = client.post("/api/vote", json={
        "content_type": "news", "content_id": "article-1", "vote": True,
    }, headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_vote_can_be_changed_without_duplicate(client):
    token = _signup(client)
    client.post("/api/vote", json={
        "content_type": "news", "content_id": "article-1", "vote": True,
    }, headers=_auth(token))
    # Flip to thumbs down — must succeed and not create a second DB row
    resp = client.post("/api/vote", json={
        "content_type": "news", "content_id": "article-1", "vote": False,
    }, headers=_auth(token))
    assert resp.status_code == 200


def test_vote_without_token_returns_403(client):
    resp = client.post("/api/vote", json={
        "content_type": "news", "content_id": "article-1", "vote": True,
    })
    assert resp.status_code == 403
