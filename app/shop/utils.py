import requests
from django.conf import settings
import os

def send_telegram_message(text: str) -> bool:
    # Получаем токен и chat_id
    token = os.getenv("BOT_TOKEN") or getattr(settings, "BOT_TOKEN", None) or getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = os.getenv("ADMIN_CHAT_ID") or getattr(settings, "ADMIN_CHAT_ID", None)

    if not token or not chat_id:
        print("⚠️ Telegram credentials not set.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ Telegram send failed: {response.status_code}, {response.text}")
            return False
        return True
    except requests.RequestException as e:
        print(f"❌ Telegram send exception: {e}")
        return False
