from decimal import Decimal
from uuid import uuid4
from rest_framework.exceptions import ValidationError
from django.db import transaction
from apps.cart.models import Cart
from apps.products.models import ProductVariant
from .models import Order,OrderItem


def generate_random_number():
    return (f"ORD-{uuid4().hex[:10].upper()}")

@transaction.atomic()
def create_order(user,shipping_data):
    cart=Cart

