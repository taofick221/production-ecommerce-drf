from .models import Cart

def get_user_cart(user):
    return  (Cart.objects.select_related("user").prefetch_related("items__variant__product",).get(user=user))
     