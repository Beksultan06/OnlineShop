from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.shop.views import (
    ProductViewSet,
    ReviewsViewSet,
    FavoriteProductViewSet,
    CartViewSet,
    CheckoutView,
    ContactAPI,
)

# 🔹 Роутер для ViewSet'ов
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewsViewSet, basename='review')
router.register(r'favorites', FavoriteProductViewSet, basename='favorite')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'contact', ContactAPI, basename='contact')

# 🔹 Основные маршруты
urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("", include(router.urls)),  # обязательно подключаем router.urls
]
