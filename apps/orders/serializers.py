from rest_framework import serializers
from .models import Order,OrderItem

class CreateOrderSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=150)
    phone=serializers.RegexField(regex=r"^\+?\d{8,15}$",
        max_length=15,trim_whitespace=True,
        error_messages={
            "invalid":
            "Enter valid phone number"
        },)
    address = serializers.CharField()

    city = serializers.CharField(max_length=100)

    postal_code = serializers.CharField(max_length=20)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:

        model = OrderItem

        fields = [
            "id",
            "product_name",
            "sku",
            "size",
            "color",
            "price",
            "quantity",
            "total_price",
        ]
        read_only_fields=fields


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True,read_only=True,)

    class Meta:

        model = Order

        fields = [
            "id",
            "order_number",
            "status",
            "payment_status",
            "subtotal",
            "total",

            "full_name",
            "phone",
            "address",
            "city",
            "postal_code",

            "items",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "order_number",

            "status",
            "payment_status",

            "subtotal",
            "total",

            "items",
            "created_at",
        ]