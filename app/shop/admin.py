from django.contrib import admin
from app.shop.models import Product, Order, ProductImage, Reviews, Report, Category
from django.utils.html import format_html
from django.db.models import Sum, Count
from datetime import timedelta, datetime
from django.utils import timezone

admin.site.register(Category)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # сколько пустых полей показывать
    max_num = 10  # максимум 10 фото
    fields = ("image",)
    verbose_name = "Фото товара"
    verbose_name_plural = "Фотографии товара"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock")      
    list_editable = ("price", "stock")                   
    search_fields = ("name",)
    inlines = [ProductImageInline]                    
    list_per_page = 20                              
    ordering = ("id",)
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "description", 'category', 'rating', 'is_favorites')
        }),
        ("Цены и наличие", {
            "fields": ("price", "stock")
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "quantity", "created_at")
    list_filter = ("created_at",)
    search_fields = ("product__name",)
    ordering = ("-created_at",)
    list_per_page = 20

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "name", "email", "rating_stars", "is_active")
    list_editable = ("is_active",)
    search_fields = ("title", "name", "email")
    list_filter = ("is_active", "rating")
    ordering = ("-id",)
    list_per_page = 20

    fieldsets = (
        ("Информация об отзыве", {
            "fields": ("title", "name", "email", "description", "rating")
        }),
        ("Статус", {
            "fields": ("is_active",)
        }),
    )

    def rating_stars(self, obj):
        """Показать звёздочки рейтинга (например, ★★★★☆)."""
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html(f"<span style='color:#f39c12;font-size:16px;'>{stars}</span>")

    rating_stars.short_description = "Оценка"

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "total_orders", "total_revenue", "created_at")
    readonly_fields = ("report_type", "total_orders", "total_revenue", "created_at")

    def has_add_permission(self, request):
        return False  # запрет добавления вручную

    def has_change_permission(self, request, obj=None):
        return False  # запрет изменения

    def has_delete_permission(self, request, obj=None):
        return False  # запрет удаления