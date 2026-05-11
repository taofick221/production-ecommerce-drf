from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.products.models import ProductVariant
from .models import Cart,CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="variant.product.name",read_only=True)
    sku=serializers.CharField(source="variant.sku",read_only=True)
    size=serializers.CharField(source="variant.size",read_only=True)
    sku=serializers.CharField(source="variant.color",read_only=True)
    unit_price=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    total_price=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    available_stock=serializers.IntegerField(source="variant.available_stock",read_only=True)

    class Meta:
        model=CartItem
        fields = [
            "id",
            "variant",
            "product_name",
            "sku",
            "size",
            "color",
            "unit_price",
            "quantity",
            "total_price",
            "available_stock",
        ]
class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(many=True,read_only=True)
    subtotal=serializers.SerializerMethodField()
    total=serializers.SerializerMethodField
    class Meta:
        model = Cart

        fields = [
            "id",
            "items",
            "subtotal",
            "total",
            "created_at",
            "updated_at",
        ]
    def get_subtotal(self,obj):
        return obj.subtotal
    def get_total(self,obj):
        return obj.total

class AddToCartSerializer(serializers.ModelSerializer):
    variant_id=serializers.IntegerField()
    quantity=serializers.IntegerField(min_value=1)
    def validate(self, attrs):
        variant_id=attrs.get("variant_id")
        quantity=attrs.get("quantity")
        try:
            variant=ProductVariant.objects.select_related("product").get(id=variant_id)

        except ProductVariant.DoesNotExist:
            raise ValidationError({"variant_id":"Variant does not exist"})
        
        if not variant.product.is_active:
            raise ValidationError({"product":"Product is inactive"})
        
        if variant.product.deleted_at:
            raise ValidationError({"product":"Product no longer available"})
        
        if quantity>variant.available_stock:
            raise ValidationError({"quantity":"Not enough stock available"})
        attrs["variant"]=variant
        return attrs
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    quantity=serializers.IntegerField(min_value=0)
    def validate_quantity(self,value):
        cart_item=self.context.get("cart_item")
        if value>cart_item.variant.available_stock:
             raise ValidationError("Not enough stock available")
        return value