from rest_framework import viewsets, filters, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta, time as dt_time
from decimal import Decimal
from django.utils import timezone
import random

from app.shop.models import Product, Reviews, Contact, Category, ModelsProduct
from app.shop.serializers import (
    ProductSerializer,
    ReviewsSerializer,
    CheckoutCreateSerializer,
    ContactSerializers,
    CheckoutOrderSerializer,
    CategorySerializers,
    ModelsProductSerializers,
)
from app.shop.filters import ProductFilter


class CategoryAPI(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializers


class ModelsProductAPI(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = ModelsProduct.objects.all()
    serializer_class = ModelsProductSerializers


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "price"]
    ordering_fields = ["price"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.order_by("?")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


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
        if not request.session.session_key:
            request.session.save()
        favorites = request.session.get("favorites", [])
        pk = int(pk)
        if pk in favorites:
            favorites.remove(pk)
            is_favorite = False
        else:
            favorites.append(pk)
            is_favorite = True
        request.session["favorites"] = favorites
        request.session.modified = True
        return Response({"product_id": pk, "is_favorite": is_favorite})

    def list(self, request, *args, **kwargs):
        ids = request.session.get("favorites", [])
        qs = Product.objects.filter(id__in=ids)
        ser = ProductSerializer(qs, many=True, context={"request": request})
        return Response(ser.data)


# ------------------- CART -------------------
class CartViewSet(viewsets.ViewSet):
    @action(detail=True, methods=["post"])
    def add(self, request, pk=None):
        cart = request.session.get("cart", {})
        product = Product.objects.get(pk=pk)
        image = product.images.first()
        image_url = request.build_absolute_uri(image.image.url) if image else None

        if str(pk) in cart:
            cart[str(pk)]["quantity"] += 1
        else:
            cart[str(pk)] = {
                "name": product.name,
                "price": float(product.price),
                "quantity": 1,
                "image": image_url,
            }

        request.session["cart"] = cart
        request.session.modified = True
        return Response(self._get_cart_summary(cart))

    @action(detail=True, methods=["post"])
    def remove(self, request, pk=None):
        cart = request.session.get("cart", {})
        if str(pk) in cart:
            del cart[str(pk)]
            request.session["cart"] = cart
            request.session.modified = True
        return Response(self._get_cart_summary(cart))

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
        return Response(self._get_cart_summary(cart))

    def list(self, request):
        cart = request.session.get("cart", {})
        return Response(self._get_cart_summary(cart))

    def _get_cart_summary(self, cart):
        total = sum(item["price"] * item["quantity"] for item in cart.values())
        return {
            "items": cart,
            "total_price": round(total, 2),
            "total_items": sum(item["quantity"] for item in cart.values()),
        }


def _compute_delivery_datetime(min_hours: int, preferred: dt_time | None):
    now = timezone.now()
    earliest = now + timedelta(hours=min_hours)
    if not preferred:
        return earliest
    candidate = earliest.replace(
        hour=preferred.hour, minute=preferred.minute, second=0, microsecond=0
    )
    if candidate < earliest:
        candidate += timedelta(days=1)
    return candidate


class CheckoutView(APIView):
    def get(self, request, *args, **kwargs):
        cart = request.session.get("cart", {})
        if not cart:
            return Response({"detail": "Корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        delivery_type = request.query_params.get("delivery_type", "standard")
        preferred_time_str = request.query_params.get("preferred_time")

        product_ids = [int(pid) for pid in cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        subtotal = Decimal("0")
        for it in cart.values():
            subtotal += Decimal(str(it["price"])) * int(it["quantity"])

        shipping_cost = Decimal("700") if delivery_type == "express" else Decimal("0")
        total = subtotal + shipping_cost

        preferred_time = None
        if preferred_time_str:
            try:
                hh, mm = preferred_time_str.split(":")
                preferred_time = dt_time(int(hh), int(mm))
            except Exception:
                return Response({"detail": "preferred_time должен быть в формате HH:MM"}, status=400)

        min_hours = 24
        delivery_dt = _compute_delivery_datetime(min_hours, preferred_time)

        base_note = "Товар будет доставлен через 24 часа."
        if preferred_time:
            delivery_note = (
                f"{base_note} Вы выбрали время {preferred_time.strftime('%H:%M')}. "
                f"Доставка назначена на {timezone.localtime(delivery_dt).strftime('%d.%m.%Y %H:%M')}."
            )
        else:
            delivery_note = (
                f"{base_note} Доставка назначена на {timezone.localtime(delivery_dt).strftime('%d.%m.%Y %H:%M')}."
            )

        items = []
        for pid_str, it in cart.items():
            pid = int(pid_str)
            product = products.get(pid)
            items.append({
                "name": it["name"],
                "price": it["price"],
                "quantity": it["quantity"],
                "line_total": round(float(it["price"]) * int(it["quantity"]), 2),
                "description_html": product.full_description_html if product else "",
                "description_text": product.full_description_text if product else "",
            })

        return Response({
            "preview": True,
            "delivery_type": delivery_type,
            "preferred_time": preferred_time.strftime("%H:%M") if preferred_time else None,
            "delivery_eta_hours": min_hours,
            "delivery_datetime": delivery_dt,
            "delivery_note": delivery_note,
            "subtotal": round(subtotal, 2),
            "shipping_cost": round(shipping_cost, 2),
            "total": round(total, 2),
            "items": items,
        })

    def post(self, request, *args, **kwargs):
        cart = request.session.get("cart", {})
        serializer = CheckoutCreateSerializer(
            data=request.data,
            context={"cart": cart, "request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(CheckoutOrderSerializer(order).data, status=status.HTTP_201_CREATED)


class ContactAPI(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializers
