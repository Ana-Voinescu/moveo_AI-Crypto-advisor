import json
import random
import httpx
from pathlib import Path
from app.schemas import MemeItem

_FALLBACK_PATH = Path(__file__).parent.parent / "static" / "fallback_memes.json"
_REDDIT_URL = "https://www.reddit.com/r/cryptocurrencymemes/hot.json"
_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif")


async def get_meme() -> MemeItem:
    try:
        async with httpx.AsyncClient(
            timeout=8.0,
            headers={"User-Agent": "crypto-dashboard/1.0"},
            follow_redirects=True,
        ) as client:
            response = await client.get(_REDDIT_URL, params={"limit": 25})
            response.raise_for_status()
            data = response.json()

        posts = [
            p["data"]
            for p in data["data"]["children"]
            if not p["data"]["is_self"]
            and p["data"].get("url", "").endswith(_IMAGE_EXTENSIONS)
            and not p["data"].get("over_18", False)
        ]

        if not posts:
            return _static_fallback()

        post = random.choice(posts)
        return MemeItem(id=post["id"], title=post["title"], url=post["url"])
    except Exception:
        return _static_fallback()


def _static_fallback() -> MemeItem:
    with open(_FALLBACK_PATH) as f:
        return MemeItem(**random.choice(json.load(f)))
