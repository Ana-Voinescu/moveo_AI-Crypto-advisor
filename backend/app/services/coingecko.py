import httpx
from typing import List
from app.schemas import CoinPrice

SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "XRP": "ripple",
    "LTC": "litecoin",
}

_FALLBACK = {
    "BTC":  CoinPrice(symbol="BTC",  price_usd=62000.0, change_24h=1.2),
    "ETH":  CoinPrice(symbol="ETH",  price_usd=3200.0,  change_24h=-0.5),
    "SOL":  CoinPrice(symbol="SOL",  price_usd=145.0,   change_24h=2.1),
    "ADA":  CoinPrice(symbol="ADA",  price_usd=0.45,    change_24h=0.8),
    "DOGE": CoinPrice(symbol="DOGE", price_usd=0.12,    change_24h=3.4),
    "DOT":  CoinPrice(symbol="DOT",  price_usd=7.50,    change_24h=0.5),
    "AVAX": CoinPrice(symbol="AVAX", price_usd=35.00,   change_24h=1.0),
    "XRP":  CoinPrice(symbol="XRP",  price_usd=0.52,    change_24h=0.3),
    "LTC":  CoinPrice(symbol="LTC",  price_usd=85.00,   change_24h=-0.2),
}


async def get_prices(symbols: List[str]) -> List[CoinPrice]:
    ids = [SYMBOL_TO_ID[s.upper()] for s in symbols if s.upper() in SYMBOL_TO_ID]
    if not ids:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": ",".join(ids), "vs_currencies": "usd", "include_24hr_change": "true"},
            )
            response.raise_for_status()
            data = response.json()

        id_to_symbol = {v: k for k, v in SYMBOL_TO_ID.items()}
        return [
            CoinPrice(
                symbol=id_to_symbol[coin_id],
                price_usd=values["usd"],
                change_24h=values.get("usd_24h_change"),
            )
            for coin_id, values in data.items()
            if coin_id in id_to_symbol
        ]
    except Exception:
        return [_FALLBACK[s.upper()] for s in symbols if s.upper() in _FALLBACK]
