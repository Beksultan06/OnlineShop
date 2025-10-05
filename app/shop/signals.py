from django.db.models.signals import post_save
from django.dispatch import receiver
from app.shop.models import Order
from django.conf import settings
from aiogram import Bot

@receiver(post_save, sender=Order)
def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        text = (
            f"🆕 Новый заказ #{instance.id}\n"
            f"📦 Товар: {instance.product.name}\n"
            f"💰 Цена: {instance.product.price}\n"
            f"🔢 Кол-во: {instance.quantity}\n"
        )
        try:
            import asyncio
            asyncio.run(bot.send_message(settings.ADMIN_CHAT_ID, text))
        except Exception as e:
            print(f"Ошибка отправки Telegram: {e}")
