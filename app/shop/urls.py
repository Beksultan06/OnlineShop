from rest_framework.routers import DefaultRouter
from django.urls import path, include
from app.shop.views import ProductViewSet, ReviewsViewSet, FavoriteProductViewSet, CartViewSet, CheckoutView, ContactAPI

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'reviews', ReviewsViewSet, basename='reviews')
router.register(r'favorites', FavoriteProductViewSet, basename='favorites')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'contact', ContactAPI, basename='contact')

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]

urlpatterns += router.urls
