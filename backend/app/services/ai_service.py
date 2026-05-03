import httpx
from datetime import date
from app.models.preferences import UserPreferences
from app import config

_FALLBACK_INSIGHTS = {
    "hodler": (
        "Patience is the HODLer's edge. Market cycles have historically rewarded those who "
        "resist reacting to short-term volatility. Consider this a quiet accumulation window."
    ),
    "day_trader": (
        "Watch volume before price today — breakouts without volume tend to fail. "
        "Keep position sizes tight and pre-define your exit before you enter."
    ),
    "nft_collector": (
        "NFT sentiment closely tracks BTC momentum. A stable or rising BTC price typically "
        "lifts appetite for digital collectibles. Blue-chip collections are holding floor prices well."
    ),
}


async def get_insight(preferences: UserPreferences) -> str:
    if not config.OPENROUTER_API_KEY:
        return _static_fallback(preferences.investor_type)

    coins = ", ".join(preferences.crypto_assets[:3])
    investor_label = preferences.investor_type.replace("_", " ").title()
    today = date.today().strftime("%B %d, %Y")
    prompt = (
        f"Today is {today}. You are a concise crypto market advisor. "
        f"The user is a {investor_label} interested in {coins}. "
        f"Reply with ONLY a 2-3 sentence daily insight — no intro, no date, no sign-off. "
        f"Focus on mindset and strategy, not specific price predictions. Be practical."
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemma-3-12b-it:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return _static_fallback(preferences.investor_type)


def _static_fallback(investor_type: str) -> str:
    return _FALLBACK_INSIGHTS.get(investor_type, _FALLBACK_INSIGHTS["hodler"])
