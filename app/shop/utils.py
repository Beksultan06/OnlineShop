import requests
import os
from django.conf import settings

def send_telegram_message(text: str):
    token = os.getenv("BOT_TOKEN", getattr(settings, "BOT_TOKEN", None))
    chat_id = os.getenv("ADMIN_CHAT_ID", getattr(settings, "ADMIN_CHAT_ID", None))

    if not token or not chat_id:
        print("⚠️ Telegram credentials not set.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    try:
        requests.post(url, data=payload, timeout=10)
        return True
    except requests.RequestException as e:
        print("Telegram send failed:", e)
        return False
