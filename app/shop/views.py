

from rest_framework import viewsets
from app.shop.models import Product, Reviews
from app.shop.serializers import ProductSerializer, ReviewsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from app.shop.filters import ProductFilter
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import generics

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    # Переопределяем list() — список товаров
    def list(self, request, *args, **kwargs):
        cache_key = "products_list"

        products = cache.get(cache_key)
        if not products:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            products = serializer.data
            cache.set(cache_key, products, timeout=60)  # кешируем на 1 минуту

        return Response(products)

    # При изменениях очищаем кеш
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

class ReviewsListCreateAPIView(generics.ListCreateAPIView):
    queryset = Reviews.objects.filter(is_active=True)
    serializer_class = ReviewsSerializer

    def get_queryset(self):
        # при GET возвращаем только активные отзывы
        if self.request.method == "GET":
            return Reviews.objects.filter(is_active=True)
        return Reviews.objects.all()