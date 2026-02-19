from typing import Optional

import httpx

from app.core.config import settings


TELEGRAM_API = "https://api.telegram.org"


def send_message(text: str) -> Optional[dict]:
    """Send a text message using bot token and chat id from settings.

    Returns the parsed JSON response if successful or None if configuration
    is missing or the request fails.
    """

    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return None

    url = f"{TELEGRAM_API}/bot{token}/sendMessage"
    try:
        resp = httpx.post(url, json={"chat_id": chat_id, "text": text})
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None
