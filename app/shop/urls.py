from rest_framework.routers import DefaultRouter
from app.shop.views import ProductViewSet, ReviewsViewSet, FavoriteProductViewSet

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'reviews', ReviewsViewSet, basename='reviews')
router.register(r'favorites', FavoriteProductViewSet, basename='favorites')

urlpatterns = router.urls
