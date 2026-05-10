from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Product, ProductImage, ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "order", "is_primary"]

    def validate(self, data):
        if data.get("order") is not None and data["order"] < 0:
            raise ValidationError("Order must be positive")
        return data


class ProductVariantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    reserved_stock = serializers.IntegerField(read_only=True)
    available_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "size",
            "color",
            "price",
            "stock",
            "reserved_stock",
            "sku",
            "is_default",
            "available_stock",
        ]

    def validate(self, data):
        price = data.get("price")
        stock = data.get("stock")
        if price is not None and price <= 0:
            raise ValidationError("Price must be positive")
        if stock is not None and stock < 0:
            raise ValidationError("Stock cannot be negative")
        return data


class ProductWriteSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True)
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "brand",
            "is_active",
            "variants",
            "images",
        ]

    def validate(self, data):
        variants = data.get("variants", [])
        errors = {}
        if not self.instance and not variants:
            raise ValidationError(
                {"variants": "At least one variant required"})
        if variants:
            cleaned = []
            for i, v in enumerate(variants):
                size = (v.get("size") or "").strip().lower()
                color = (v.get("color") or "").strip().lower()
                sku = (v.get("sku") or "").strip().upper()
                is_default = bool(v.get("is_default"))
                v["size"] = size
                v["color"] = color
                v["sku"] = sku
                v["is_default"] = is_default
                if not size:
                    errors[f"variant_{i}_size"] = "Size required"
                if not color:
                    errors[f"variant_{i}_color"] = "Color required"
                if not sku:
                    errors[f"variant_{i}_sku"] = "SKU required"

                cleaned.append((size, color, sku, is_default))
            if sum(1 for _, _, _, d in cleaned if d) != 1:
                errors["default"] = "Exactly one default variant required"
            skus = [sku for _, _, sku, _ in cleaned if sku]
            if len(skus) != len(set(skus)):
                errors["sku"] = "Duplicate SKU found"
            combos = [(size, color)
                      for size, color, _, _ in cleaned if size and color]
            if len(combos) != len(set(combos)):
                errors["variant_combination"] = "Dublicate size and color found"
            if errors:
                raise ValidationError(errors)
        return data

    def create(self, validated_data):
        from .services import create_product
        return create_product(validated_data)

    def update(self, instance, validated_data):
        from .services import update_product
        return update_product(instance, validated_data)


class ProductReadSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "brand",
            "is_active",
            "created_at",
            "variants",
            "images",
        ]
