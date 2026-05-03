import json
import httpx
from pathlib import Path
from typing import List
from app.schemas import NewsItem
from app import config

_FALLBACK_PATH = Path(__file__).parent.parent / "static" / "fallback_news.json"


async def get_news(symbols: List[str]) -> List[NewsItem]:
    if not config.CRYPTOPANIC_API_KEY:
        return _static_fallback()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://cryptopanic.com/api/v1/posts/",
                params={
                    "auth_token": config.CRYPTOPANIC_API_KEY,
                    "currencies": ",".join(symbols),
                    "kind": "news",
                },
            )
            response.raise_for_status()
            data = response.json()

        return [
            NewsItem(
                id=str(item["id"]),
                title=item["title"],
                url=item["url"],
                source=item["source"]["title"],
            )
            for item in data.get("results", [])[:5]
        ]
    except Exception:
        return _static_fallback()


def _static_fallback() -> List[NewsItem]:
    with open(_FALLBACK_PATH) as f:
        return [NewsItem(**item) for item in json.load(f)]
