import json
import httpx
from pathlib import Path
from typing import List
from app.schemas import NewsItem
from app import config

_FALLBACK_PATH = Path(__file__).parent.parent / "static" / "fallback_news.json"


async def get_news(symbols: List[str]) -> List[NewsItem]:
    if not config.NEWSDATA_API_KEY:
        return _static_fallback()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://newsdata.io/api/1/crypto",
                params={
                    "apikey": config.NEWSDATA_API_KEY,
                    "q": " OR ".join(symbols),
                    "language": "en",
                },
            )
            response.raise_for_status()
            data = response.json()

        return [
            NewsItem(
                id=item["article_id"],
                title=item["title"],
                url=item["link"],
                source=item["source_name"],
            )
            for item in data.get("results", [])
        ]
    except Exception:
        return _static_fallback()


def _static_fallback() -> List[NewsItem]:
    with open(_FALLBACK_PATH) as f:
        return [NewsItem(**item) for item in json.load(f)]
