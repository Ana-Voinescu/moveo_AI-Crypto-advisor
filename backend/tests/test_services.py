"""
Fallback logic tests for all four external services.

Each test either:
  (a) mocks a successful HTTP response and checks the data is parsed correctly, or
  (b) makes the HTTP call fail and checks that static fallback data is returned.

_MockHttpClient is a reusable helper that acts like httpx.AsyncClient
as an async context manager, so the service code needs no changes.
"""
from unittest.mock import patch, MagicMock
from app.services import coingecko, cryptopanic, ai_service, meme_service
from app.schemas import CoinPrice, NewsItem, MemeItem
from app import config


class _MockHttpClient:
    """Behaves like `async with httpx.AsyncClient() as client`."""

    def __init__(self, response_data=None, raise_exc=None):
        self._data = response_data
        self._exc = raise_exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def _make_response(self):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value=self._data)
        return resp

    async def get(self, *args, **kwargs):
        if self._exc:
            raise self._exc
        return self._make_response()

    async def post(self, *args, **kwargs):
        if self._exc:
            raise self._exc
        return self._make_response()


# ============================================================
# CoinGecko
# ============================================================

async def test_coingecko_parses_live_response():
    fake_data = {
        "bitcoin": {"usd": 62000.0, "usd_24h_change": 1.5},
        "ethereum": {"usd": 3100.0, "usd_24h_change": -0.3},
    }
    with patch("app.services.coingecko.httpx.AsyncClient",
               return_value=_MockHttpClient(response_data=fake_data)):
        result = await coingecko.get_prices(["BTC", "ETH"])

    assert any(p.symbol == "BTC" and p.price_usd == 62000.0 for p in result)
    assert any(p.symbol == "ETH" and p.change_24h == -0.3 for p in result)


async def test_coingecko_returns_fallback_on_network_error():
    with patch("app.services.coingecko.httpx.AsyncClient",
               return_value=_MockHttpClient(raise_exc=Exception("timeout"))):
        result = await coingecko.get_prices(["BTC", "ETH"])

    assert len(result) > 0
    assert all(isinstance(p, CoinPrice) for p in result)


async def test_coingecko_returns_empty_for_unknown_symbols():
    # Unknown symbols have no CoinGecko ID mapping — should return empty, not crash
    result = await coingecko.get_prices(["FAKECOIN", "XYZ"])
    assert result == []


# ============================================================
# CryptoPanic
# ============================================================

async def test_cryptopanic_uses_fallback_when_no_api_key(monkeypatch):
    monkeypatch.setattr(config, "CRYPTOPANIC_API_KEY", "")
    result = await cryptopanic.get_news(["BTC"])
    assert len(result) > 0
    assert all(isinstance(n, NewsItem) for n in result)


async def test_cryptopanic_returns_fallback_on_network_error(monkeypatch):
    monkeypatch.setattr(config, "CRYPTOPANIC_API_KEY", "fake-key")
    with patch("app.services.cryptopanic.httpx.AsyncClient",
               return_value=_MockHttpClient(raise_exc=Exception("connection refused"))):
        result = await cryptopanic.get_news(["BTC"])

    assert len(result) > 0
    assert all(isinstance(n, NewsItem) for n in result)


async def test_cryptopanic_parses_live_response(monkeypatch):
    monkeypatch.setattr(config, "CRYPTOPANIC_API_KEY", "fake-key")
    fake_data = {
        "results": [
            {"id": 1, "title": "BTC hits ATH", "url": "http://news.com/btc",
             "source": {"title": "CoinDesk"}},
        ]
    }
    with patch("app.services.cryptopanic.httpx.AsyncClient",
               return_value=_MockHttpClient(response_data=fake_data)):
        result = await cryptopanic.get_news(["BTC"])

    assert len(result) == 1
    assert result[0].title == "BTC hits ATH"
    assert result[0].source == "CoinDesk"
    assert result[0].id == "1"


# ============================================================
# AI Service
# ============================================================

async def test_ai_returns_fallback_when_no_api_key(monkeypatch):
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "")

    class _Prefs:
        investor_type = "hodler"
        crypto_assets = ["BTC"]

    result = await ai_service.get_insight(_Prefs())
    assert isinstance(result, str) and len(result) > 10


async def test_ai_returns_fallback_on_api_error(monkeypatch):
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "fake-key")

    class _Prefs:
        investor_type = "day_trader"
        crypto_assets = ["ETH"]

    with patch("app.services.ai_service.httpx.AsyncClient",
               return_value=_MockHttpClient(raise_exc=Exception("rate limited"))):
        result = await ai_service.get_insight(_Prefs())

    assert isinstance(result, str) and len(result) > 10


async def test_ai_fallback_covers_all_investor_types(monkeypatch):
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "")
    for investor_type in ["hodler", "day_trader", "nft_collector"]:
        class _Prefs:
            pass
        prefs = _Prefs()
        prefs.investor_type = investor_type
        prefs.crypto_assets = ["BTC"]
        result = await ai_service.get_insight(prefs)
        assert isinstance(result, str) and len(result) > 0, \
            f"No fallback insight for investor_type='{investor_type}'"


async def test_ai_parses_live_openrouter_response(monkeypatch):
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "fake-key")
    fake_data = {"choices": [{"message": {"content": "  BTC looks strong today.  "}}]}

    class _Prefs:
        investor_type = "hodler"
        crypto_assets = ["BTC"]

    with patch("app.services.ai_service.httpx.AsyncClient",
               return_value=_MockHttpClient(response_data=fake_data)):
        result = await ai_service.get_insight(_Prefs())

    assert result == "BTC looks strong today."  # whitespace stripped


# ============================================================
# Meme Service
# ============================================================

async def test_meme_returns_fallback_on_network_error():
    with patch("app.services.meme_service.httpx.AsyncClient",
               return_value=_MockHttpClient(raise_exc=Exception("reddit down"))):
        result = await meme_service.get_meme()

    assert isinstance(result, MemeItem)
    assert result.url.startswith("http")


async def test_meme_parses_image_post_from_reddit():
    fake_data = {
        "data": {
            "children": [
                {"data": {"id": "abc", "title": "When BTC moons",
                          "is_self": False, "url": "http://i.redd.it/meme.jpg",
                          "over_18": False}},
            ]
        }
    }
    with patch("app.services.meme_service.httpx.AsyncClient",
               return_value=_MockHttpClient(response_data=fake_data)):
        result = await meme_service.get_meme()

    assert result.id == "abc"
    assert result.title == "When BTC moons"
    assert result.url.endswith(".jpg")


async def test_meme_skips_text_posts_and_uses_fallback():
    # All posts are text posts (is_self=True) — no valid image, should fall back
    fake_data = {
        "data": {
            "children": [
                {"data": {"id": "x1", "title": "Discussion post",
                          "is_self": True, "url": "http://reddit.com/post",
                          "over_18": False}},
            ]
        }
    }
    with patch("app.services.meme_service.httpx.AsyncClient",
               return_value=_MockHttpClient(response_data=fake_data)):
        result = await meme_service.get_meme()

    assert isinstance(result, MemeItem)  # static fallback was used
