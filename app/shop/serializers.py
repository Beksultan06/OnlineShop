from rest_framework import serializers
from app.shop.models import Product, Order, ProductImage, Reviews, Category

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

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "images", 'rating', 'is_favorites', 'category']

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