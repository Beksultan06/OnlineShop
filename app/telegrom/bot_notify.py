import os
import asyncio
import logging
from aiogram import Bot
from aiohttp import ClientTimeout
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN") or "8420115725:AAGhOwGmXk4S2GDO-MhEAU9tGtIhITiYpeE"
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID") or 5199401134

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, timeout=ClientTimeout(total=60))


def send_order_notification(order_data: dict):
    """Синхронная отправка уведомления о новом заказе через aiogram"""
    async def _send():
        text = (
    f"🛒 Новый заказ!\n"
    f"👤 Клиент: {order_data.get('user_name')}\n"
    f"📧 Email: {order_data.get('email')}\n"
    f"📞 Телефон: {order_data.get('user_phone')}\n"
    f"🏠 Адрес: {order_data.get('user_address')}\n"
    f"🛍️ Товары: {order_data.get('product_name')}\n"
    f"Количество: {order_data.get('quantity')}"
)

        try:
            await bot.send_message(ADMIN_CHAT_ID, text=text)
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления: {e}")
        finally:
            await bot.session.close()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_send())
    loop.close()
