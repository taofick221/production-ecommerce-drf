from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.products.models import ProductVariant
from .models import Cart,CartItem

@transaction.atomic()
def get_or_create_cart(user):
    cart, _=Cart.objects.get_or_create(user=user)
    return cart

@transaction.atomic()
def add_to_cart(user,variant,quantity):
    variant=ProductVariant.objects.select_for_update().select_related("product").get(id=variant.id)
    if not variant.product.is_active:
        raise ValidationError({"product":"Product is inactive"})
    if not variant.product.deleted_at:
        raise ValidationError({"product":"Product no longer available"})
    
    cart=get_or_create_cart(user)
    cart_item,created=(CartItem.objects.get_or_create(cart=cart,variant=variant,defaults={"quantity":quantity}))
    if not created:
        new_quantity=cart_item.quantity+quantity
        if new_quantity>variant.available_stock:
            raise ValidationError({"quantity":"Not enough stock available"})
        cart_item.quantity=new_quantity
        cart_item.save()
    return cart

@transaction.atomic()
def update_cart_item(cart_item,quantity):
    variant=ProductVariant.objects.select_for_update().get(id=cart_item.variant.id)
    if quantity<0:
        raise ValidationError({"quantity":"Quantity cannot be negative"})
    if quantity==0:
        cart_item.delete()
        return
    if quantity > variant.available_stock:
        raise ValidationError({"quantity":"Not enough stock available"})
    cart_item.quantity=quantity
    cart_item.save()
    return cart_item

@transaction.atomic()
def remove_cart_item(cart_item):
    cart_item.delete()

@transaction.atomic()
def clear_cart(cart):
    cart.items.all().delete()