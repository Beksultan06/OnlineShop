# from django.contrib import admin
# from app.shop.models import Product, Order, ProductImage, Reviews, Report, Category, CheckoutOrder, CheckoutItem, Visit, Contact
# from django.utils.html import format_html
# from django.db.models import Sum, Count
# from datetime import timedelta, datetime
# from django.utils import timezone

# admin.site.register(Category)
# admin.site.register(Contact)

# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1  
#     max_num = 10  
#     fields = ("image",)
#     verbose_name = "Фото товара"
#     verbose_name_plural = "Фотографии товара"


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "price", "stock")      
#     list_editable = ("price", "stock")                   
#     search_fields = ("name",)
#     inlines = [ProductImageInline]                    
#     list_per_page = 20                              
#     ordering = ("id",)
#     fieldsets = (
#         ("Основная информация", {
#             "fields": ("name", "description", 'category', 'rating', 'is_favorites')
#         }),
#         ("Цены и наличие", {
#             "fields": ("price", "stock")
#         }),
#     )


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("id", "product", "quantity", "created_at")
#     list_filter = ("created_at",)
#     search_fields = ("product__name",)
#     ordering = ("-created_at",)
#     list_per_page = 20

# @admin.register(Reviews)
# class ReviewsAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "name", "email", "rating_stars", "is_active")
#     list_editable = ("is_active",)
#     search_fields = ("title", "name", "email")
#     list_filter = ("is_active", "rating")
#     ordering = ("-id",)
#     list_per_page = 20

#     fieldsets = (
#         ("Информация об отзыве", {
#             "fields": ("title", "name", "email", "description", "rating")
#         }),
#         ("Статус", {
#             "fields": ("is_active",)
#         }),
#     )

#     def rating_stars(self, obj):
#         """Показать звёздочки рейтинга (например, ★★★★☆)."""
#         stars = "★" * obj.rating + "☆" * (5 - obj.rating)
#         return format_html(f"<span style='color:#f39c12;font-size:16px;'>{stars}</span>")

#     rating_stars.short_description = "Оценка"

# @admin.register(Report)
# class ReportAdmin(admin.ModelAdmin):
#     list_display = ("report_type", "total_orders", "total_revenue", "created_at")
#     readonly_fields = ("report_type", "total_orders", "total_revenue", "created_at")

#     def has_add_permission(self, request):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False  

# class CheckoutItemInline(admin.TabularInline):
#     model = CheckoutItem
#     extra = 0
#     readonly_fields = ("product", "quantity", "price", "line_total")

# @admin.register(CheckoutOrder)
# class CheckoutOrderAdmin(admin.ModelAdmin):
#     list_display = ("id", "first_name", "phone", "delivery_type", "total", "delivery_datetime", "created_at")
#     list_filter = ("delivery_type", "created_at")
#     search_fields = ("first_name", "last_name", "email", "phone", "city", "address")
#     readonly_fields = (
#         "shipping_cost", "subtotal", "total",
#         "delivery_eta_hours", "preferred_time", "delivery_datetime", "delivery_note", "created_at"
#     )
#     inlines = [CheckoutItemInline]

# admin.site.register(Visit)
from django.contrib import admin
from app.shop.models import (
    Product, CheckoutOrder, CheckoutItem, Category, Contact, Visit
)

# Категории, контакты, посещения
admin.site.register(Category)
admin.site.register(Contact)
admin.site.register(Visit)

# Inline для товаров в заказе
class CheckoutItemInline(admin.TabularInline):
    model = CheckoutItem
    fk_name = "order"
    extra = 0
    readonly_fields = ("product_name", "quantity", "price", "line_total_display")
    can_delete = False
    verbose_name = "Товар"
    verbose_name_plural = "Товары в заказе"

    def product_name(self, obj):
        return obj.product.name if obj.product else "-"
    product_name.short_description = "Товар"

    def line_total_display(self, obj):
        return f"{obj.line_total:.2f} сом"
    line_total_display.short_description = "Сумма"


# CheckoutOrder admin
@admin.register(CheckoutOrder)
class CheckoutOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "phone", "delivery_type", "total_sum", "created_at")
    list_filter = ("delivery_type", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "city", "address")
    readonly_fields = (
        "shipping_cost", "subtotal", "total",
        "delivery_eta_hours", "preferred_time", "delivery_datetime",
        "delivery_note", "created_at",
    )
    inlines = [CheckoutItemInline]

    fieldsets = (
        ("Информация о клиенте", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("Адрес доставки", {"fields": ("city", "address", "country", "postcode")}),
        ("Доставка", {"fields": ("delivery_type", "delivery_eta_hours", "preferred_time", "delivery_datetime")}),
        ("Стоимость", {"fields": ("subtotal", "shipping_cost", "total")}),
        ("Примечания", {"fields": ("note", "delivery_note")}),
        ("Системная информация", {"fields": ("created_at",)}),
    )
