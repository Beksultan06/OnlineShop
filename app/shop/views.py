from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache

from app.shop.models import Product, Reviews
from app.shop.serializers import ProductSerializer, ReviewsSerializer
from app.shop.filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    def list(self, request, *args, **kwargs):
        cache_key = "products_list"
        products = cache.get(cache_key)

        if not products:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            products = serializer.data
            cache.set(cache_key, products, timeout=60)

        return Response(products)

    def perform_create(self, serializer):
        product = serializer.save()
        cache.delete("products_list")
        return product

    def perform_update(self, serializer):
        product = serializer.save()
        cache.delete("products_list")
        return product

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("products_list")


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == "GET":
            queryset = queryset.filter(is_active=True)
        return queryset
