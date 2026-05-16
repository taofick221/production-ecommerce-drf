from .models import Order

def get_user_orders(user):
    return (Order.objects.select_related("user").prefetch_related("items","items__variant")).filter(user=user)
