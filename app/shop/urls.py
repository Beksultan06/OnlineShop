from rest_framework.routers import DefaultRouter
from app.shop.views import ProductViewSet, ReviewsViewSet

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'reviews', ReviewsViewSet, basename='reviews')

urlpatterns = router.urls
