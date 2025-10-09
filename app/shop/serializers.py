from rest_framework import serializers
from app.shop.models import Product, Order, ProductImage, Reviews, Category, CheckoutOrder, CheckoutItem, Contact
from decimal import Decimal
from datetime import timedelta, time as dt_time   
from django.utils import timezone
from django.db import transaction
from app.shop.utils import send_telegram_message

class ContactSerializers(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active']

class ProductImageSerializer(serializers.ModelSerializer):    
    class Meta:
        model = ProductImage
        fields = ["id", "image"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    category = CategorySerializers(read_only=True)
    is_favorites = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "images", "rating", "is_favorites", "category"]

    def get_is_favorites(self, obj):
        request = self.context.get("request")
        if request:
            favorites = request.session.get("favorites", [])
            return obj.id in favorites
        return False

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)

        for image_data in images_data[:10]:
            ProductImage.objects.create(product=product, **image_data)
        return product

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = "__all__"
        read_only_fields = ("is_active",)


class CheckoutItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CheckoutItem
        fields = ("product", "product_name", "price", "quantity", "line_total")


class CheckoutOrderSerializer(serializers.ModelSerializer):
    items = CheckoutItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = CheckoutOrder
        fields = (
            "id", "first_name", "last_name", "email", "phone",
            "delivery_type", "country", "city", "address", "postcode",
            "note", "shipping_cost", "subtotal", "total",
            "delivery_eta_hours", "preferred_time", "delivery_datetime", "delivery_note",
            "created_at", "items"
        )


class CheckoutCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    delivery_type = serializers.ChoiceField(choices=CheckoutOrder.DELIVERY_CHOICES)
    preferred_time = serializers.TimeField(required=False, allow_null=True) 
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=255)
    postcode = serializers.CharField(max_length=20, required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)

    @staticmethod
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

    def validate(self, attrs):
        cart = self.context.get("cart") or {}
        if not cart:
            raise serializers.ValidationError("Корзина пуста.")
        ids = [int(k) for k in cart.keys()]
        exists = Product.objects.filter(id__in=ids).count()
        if exists != len(ids):
            raise serializers.ValidationError("В корзине есть недоступные товары.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        cart = (self.context.get("cart") or {}).copy()

        shipping_cost = Decimal("0")
        if validated_data["delivery_type"] == CheckoutOrder.DELIVERY_EXPRESS:
            shipping_cost = Decimal("700")

        product_ids = [int(pid) for pid in cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        subtotal = Decimal("0")
        items_payload = []
        for pid_str, it in cart.items():
            pid = int(pid_str)
            qty = int(it["quantity"])
            price = Decimal(str(it["price"]))
            line_total = price * qty
            subtotal += line_total
            items_payload.append((pid, price, qty, line_total))

        total = subtotal + shipping_cost
        min_hours = 24
        preferred_time = validated_data.get("preferred_time")
        delivery_dt = self._compute_delivery_datetime(min_hours, preferred_time)

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

        with transaction.atomic():
            order = CheckoutOrder.objects.create(
                first_name=validated_data["first_name"],
                last_name=validated_data.get("last_name", ""),
                email=validated_data["email"],
                phone=validated_data["phone"],
                delivery_type=validated_data["delivery_type"],
                country=validated_data["country"],
                city=validated_data["city"],
                address=validated_data["address"],
                postcode=validated_data.get("postcode", ""),
                note=validated_data.get("note", ""),
                shipping_cost=shipping_cost,
                subtotal=subtotal,
                total=total,
                delivery_eta_hours=min_hours,
                preferred_time=preferred_time,
                delivery_datetime=delivery_dt,
                delivery_note=delivery_note,
            )

            CheckoutItem.objects.bulk_create([
                CheckoutItem(
                    order=order,
                    product=products[int(pid)],
                    price=price,
                    quantity=qty,
                    line_total=line_total,
                )
                for pid, price, qty, line_total in items_payload
            ])
        msg_lines = [
            f"🛒 <b>Новый заказ #{order.id}</b>",
            f"👤 {order.first_name} {order.last_name}",
            f"📞 {order.phone}",
            f"📧 {order.email}",
            "",
            f"🏙️ {order.country}, {order.city}",
            f"📦 Адрес: {order.address}",
            f"🚚 Тип доставки: {order.delivery_type}",
            f"⏰ {order.delivery_note}",
            "",
            "<b>Товары:</b>",
        ]

        for pid_str, it in cart.items():
            msg_lines.append(
                f"• {it['name']} — {it['quantity']} шт × {it['price']} ₽"
            )

        msg_lines.append("")
        msg_lines.append(f"💰 <b>Итого: {order.total} ₽</b>")

        send_telegram_message("\n".join(msg_lines))  

        if request is not None:
            request.session["cart"] = {}
            request.session.modified = True

        return order