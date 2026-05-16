from .models import Order

def get_user_orders(user):
    return (Order.objects.select_related("user").prefetch_related("items","items__variant")).filter(user=user)


def get_user_orders_by_id(user,order_id):
    return (Order.objects.select_related("user").prefetch_related("items","items__variant")).get(id=order_id,user=user)


