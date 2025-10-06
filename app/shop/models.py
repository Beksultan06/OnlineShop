from django.db import models
from django.utils import timezone
from django.db.models import Sum, F
from datetime import timedelta
from ckeditor.fields import RichTextField


RATING_CHOICES = [
        (1, "★☆☆☆☆ (1)"),
        (2, "★★☆☆☆ (2)"),
        (3, "★★★☆☆ (3)"),
        (4, "★★★★☆ (4)"),
        (5, "★★★★★ (5)"),
    ]

class Category(models.Model):
    name = models.CharField(
        max_length=155,
        verbose_name='Категория'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='В наличий'
    )
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='categories'
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название товара"
    )
    description = RichTextField(
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
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        verbose_name="Оценка (1–5)"
    )
    is_favorites = models.BooleanField(
        default=False,
        verbose_name='В ИЗБРАННОЕ'
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

class Reviews(models.Model):
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
    user_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Имя клиента"
    )
    user_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон"
    )
    user_address = models.TextField(
        blank=True,
        verbose_name="Адрес доставки"
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
        return f"Заказ №{self.id} - {self.product.name}"