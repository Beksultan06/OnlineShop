from django.urls import path

from rest_framework.routers import DefaultRouter
from app.shop.views import ProductViewSet, ReviewsListCreateAPIView

router = DefaultRouter()
router.register(r'product',ProductViewSet, basename='product-list')

urlpatterns = [
    path("reviews/", ReviewsListCreateAPIView.as_view(), name="reviews-list-create"),
]

urlpatterns += router.urls