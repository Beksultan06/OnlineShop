from rest_framework.routers import DefaultRouter
from app.shop.views import ProductViewSet, ReviewsViewSet, FavoriteProductViewSet, CartViewSet

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'reviews', ReviewsViewSet, basename='reviews')
router.register(r'favorites', FavoriteProductViewSet, basename='favorites')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = router.urls