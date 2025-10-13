# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from app.shop.models import Order
# from django.conf import settings
# from aiogram import Bot

# @receiver(post_save, sender=Order)
# def send_telegram_notification(sender, instance, created, **kwargs):
#     if created:
#         bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
#         text = (
#             f"🆕 Новый заказ #{instance.id}\n"
#             f"📦 Товар: {instance.product.name}\n"
#             f"💰 Цена: {instance.product.price}\n"
#             f"🔢 Кол-во: {instance.quantity}\n"
#         )
#         try:
#             import asyncio
#             asyncio.run(bot.send_message(settings.ADMIN_CHAT_ID, text))
#         except Exception as e:
#             print(f"Ошибка отправки Telegram: {e}")

from django.db.models.signals import post_save
from django.dispatch import receiver
from app.shop.models import CheckoutOrder
from app.telegrom.bot_notify import send_order_notification

@receiver(post_save, sender=CheckoutOrder)
def notify_new_checkout_order(sender, instance, created, **kwargs):
    if created:
        # Формируем данные для уведомления
        product_names = ", ".join([item.product.name for item in instance.items.all()])
        total_quantity = sum([item.quantity for item in instance.items.all()])

        order_data = {
            "user_name": f"{instance.first_name} {instance.last_name}".strip(),
            "user_phone": instance.phone,
            "user_address": f"{instance.city}, {instance.address}",
            "product_name": product_names,
            "quantity": total_quantity,
        }

        # Отправляем уведомление
        send_order_notification(order_data)
