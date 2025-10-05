from django.db import models
from django.utils import timezone
from django.db.models import Sum, F
from datetime import timedelta

class Product(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название товара"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество на складе"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["id"]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар"
    )
    image = models.ImageField(
        upload_to="products/",
        verbose_name="Изображение"
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self):
        return f"Изображение для {self.product.name}"


class Order(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.id}"


class Reviews(models.Model):
    RATING_CHOICES = [
        (1, "★☆☆☆☆ (1)"),
        (2, "★★☆☆☆ (2)"),
        (3, "★★★☆☆ (3)"),
        (4, "★★★★☆ (4)"),
        (5, "★★★★★ (5)"),
    ]

    title = models.CharField(
        max_length=155,
        verbose_name="Заголовок"
    )
    name = models.CharField(
        max_length=155,
        verbose_name="Имя"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Активен"
    )
    email = models.CharField(
        max_length=155,
        verbose_name="Почта"
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        verbose_name="Оценка (1–5)"
    )

    def __str__(self):
        return f"{self.title} — {self.rating}★"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-id"]

class Report(models.Model):
    REPORT_TYPES = [
        ('daily', 'Дневной отчёт'),
        ('weekly', 'Недельный отчёт'),
        ('monthly', 'Месячный отчёт'),
    ]

    report_type = models.CharField(
        max_length=10,
        choices=REPORT_TYPES,
        verbose_name="Тип отчёта"
    )
    total_orders = models.PositiveIntegerField(
        verbose_name="Количество заказов"
    )
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Общая выручка"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания отчёта"
    )

    class Meta:
        verbose_name = "Отчёт"
        verbose_name_plural = "Отчёты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_report_type_display()} — {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @classmethod
    def generate_reports(cls):
        """Создаёт дневной, недельный и месячный отчёты"""
        from .models import Order

        now = timezone.now()

        periods = {
            'daily': now - timedelta(days=1),
            'weekly': now - timedelta(weeks=1),
            'monthly': now - timedelta(days=30),
        }

        for report_type, start_date in periods.items():
            orders = Order.objects.filter(created_at__gte=start_date)

            total_orders = orders.count()
            total_revenue = (
                orders.aggregate(total=Sum(F('product__price') * F('quantity')))["total"] or 0
            )

            cls.objects.create(
                report_type=report_type,
                total_orders=total_orders,
                total_revenue=total_revenue
            )