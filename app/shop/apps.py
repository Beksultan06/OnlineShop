
from django.apps import AppConfig

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.shop'

    def ready(self):
        # Подключаем сигналы
        import app.shop.signals
