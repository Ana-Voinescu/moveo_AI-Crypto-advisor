# Add External API Service with Static Fallback

Add a new external API service to the FastAPI backend following the project's established pattern.

## What to ask the user before starting

1. What is the name of the service? (e.g. coingecko, cryptopanic)
2. What is the external API endpoint URL?
3. Does it require an API key? If yes, what environment variable name should hold it?
4. What data does it return? (describe the response fields)
5. Do you want a static JSON fallback file, or a hardcoded fallback inside the service?

## Steps to implement

### 1. Create the service file at `backend/app/services/<name>.py`

Follow this structure exactly:

```python
import httpx
from app import config
from app.schemas import <ReturnType>

# If the service requires an API key, check config.<API_KEY_VAR>
# If it is empty, skip the live call and go straight to fallback

async def get_<data>(params) -> <ReturnType>:
    if not config.<API_KEY_VAR>:          # skip if key missing (optional step)
        return _static_fallback()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(URL, params={...}, headers={...})
            response.raise_for_status()
            data = response.json()
        return _parse(data)
    except Exception:
        return _static_fallback()


def _static_fallback() -> <ReturnType>:
    # Either load from a JSON file in app/static/ or return hardcoded values
    ...
```

Key rules:
- Always use `async def` and `await` so FastAPI can run calls in parallel with `asyncio.gather`
- Always wrap the HTTP call in `try/except Exception` — network errors, timeouts, bad status codes all fall through to the fallback
- Never let an exception from an external API crash the dashboard endpoint
- The fallback must return the same type as the live path

### 2. If using a JSON fallback file

Create `backend/app/static/<name>_fallback.json` with realistic sample data matching the schema.

Load it like this:
```python
import json
from pathlib import Path

FALLBACK_PATH = Path(__file__).parent.parent / "static" / "<name>_fallback.json"

def _static_fallback():
    with open(FALLBACK_PATH) as f:
        items = json.load(f)
    return [Schema(**item) for item in items]
```

### 3. Add any new env variable to config and .env.example

In `backend/app/config.py`:
```python
NEW_API_KEY = os.getenv("NEW_API_KEY", "")
```

In `backend/.env.example`:
```
NEW_API_KEY=your-key-here
```

### 4. Call the service from the router

Import and call the service in the relevant router (e.g. `dashboard.py`).
Use `asyncio.gather` if calling multiple services in parallel.
Never query the external API directly from the router.

### 5. Add a test

In `backend/tests/`, add a test that:
- Patches the HTTP call to return mock data and asserts the service parses it correctly
- Confirms the fallback is returned when the HTTP call raises an exception
