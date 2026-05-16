from decimal import Decimal
from uuid import uuid4
from rest_framework.exceptions import ValidationError
from django.db import transaction
from apps.cart.models import Cart
from apps.products.models import ProductVariant
from .models import Order,OrderItem


def generate_order_number():
    return (f"ORD-{uuid4().hex[:10].upper()}")

@transaction.atomic()
def create_order(user,shipping_data):
    cart=Cart.objects.prefetch_related(
        "items",
        "items__variant",
        "items__variant__product",
    ).get(user=user)

    if not cart.items.exists():
        raise ValidationError({"cart": "Cart is empty"})
    
    subtotal=Decimal("0.00")

    order=Order.objects.create(
        user=user,
        order_number=generate_order_number(),
        full_name=shipping_data["full_name"],
        phone=shipping_data["phone"],
        address=shipping_data["address"],
        city=shipping_data["city"],
        postal_code=shipping_data["postal_code"],
    )

    order_items=[]
    for item in cart.items.all():
        variant=ProductVariant.objects.select_for_update().select_related("product").get(id=item.variant.id)
        if not variant.product.is_active:
            raise ValidationError({"product":f"{variant.product.name} inactive"})
        if variant.product.deleted_at:
            raise ValidationError({"product":f"{variant.product.name} unavailable"})
        if item.quantity>variant.available_stock:
            raise ValidationError({
                "stock":
                f"Not enough stock "
                f"for {variant.sku}"
            })
        total_price=(variant.price*item.quantity)
        subtotal+=total_price

        order_items.append(
            OrderItem(
                order=order,
                variant=variant,

                product_name=(
                    variant.product.name
                ),

                sku=variant.sku,

                size=variant.size,

                color=variant.color,

                price=variant.price,

                quantity=item.quantity,

                total_price=total_price,
            )
        )
        variant.stock-=item.quantity
        variant.save(update_fields=["stock"])

    OrderItem.objects.bulk_create(order_items)
    order.subtotal=subtotal
    order.total=subtotal
    order.save(update_fields=["subtotal","total",])
    cart.items.all().delete()
    return order
