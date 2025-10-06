from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework.decorators import action
from rest_framework.response import Response

from app.shop.models import Product, Reviews
from app.shop.serializers import ProductSerializer, ReviewsSerializer
from app.shop.filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", 'price']
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

class FavoriteProductViewSet(viewsets.ViewSet):
    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        favorites = request.session.get("favorites", [])

        if int(pk) in favorites:
            favorites.remove(int(pk))
            is_favorite = False
        else:
            favorites.append(int(pk))
            is_favorite = True

        request.session["favorites"] = favorites
        request.session.modified = True

        return Response({"product_id": pk, "is_favorite": is_favorite})

    @action(detail=False, methods=["get"])
    def list(self, request):
        favorites_ids = request.session.get("favorites", [])
        queryset = Product.objects.filter(id__in=favorites_ids)
        serializer = ProductSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


class CartViewSet(viewsets.ViewSet):
    @action(detail=True, methods=["post"])
    def add(self, request, pk=None):
        cart = request.session.get("cart", {})
        product = Product.objects.get(pk=pk)

        if str(pk) in cart:
            cart[str(pk)]["quantity"] += 1
        else:
            cart[str(pk)] = {
                "name": product.name,
                "price": float(product.price),
                "quantity": 1
            }

        request.session["cart"] = cart
        request.session.modified = True
        return Response(cart)

    @action(detail=True, methods=["post"])
    def remove(self, request, pk=None):
        cart = request.session.get("cart", {})
        if str(pk) in cart:
            del cart[str(pk)]
            request.session["cart"] = cart
            request.session.modified = True
        return Response(cart)

    @action(detail=True, methods=["post"])
    def decrement(self, request, pk=None):
        cart = request.session.get("cart", {})
        if str(pk) in cart:
            if cart[str(pk)]["quantity"] > 1:
                cart[str(pk)]["quantity"] -= 1
            else:
                del cart[str(pk)]
            request.session["cart"] = cart
            request.session.modified = True
        return Response(cart)

    @action(detail=False, methods=["get"])
    def list(self, request):
        cart = request.session.get("cart", {})
        return Response(cart)