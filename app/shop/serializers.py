from rest_framework import serializers
from app.shop.models import Product, Order, ProductImage, Reviews


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "images"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)

        # Добавляем максимум 10 изображений
        for image_data in images_data[:10]:
            ProductImage.objects.create(product=product, **image_data)

        return product


class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = "__all__"
        read_only_fields = ("is_active",)