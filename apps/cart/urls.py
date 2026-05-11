from django.urls import path

from .views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)

urlpatterns = [

    path("",CartView.as_view(),name="cart",),

    path("add/",AddToCartView.as_view(),name="add_to_cart",),

    path("items/<int:item_id>/",UpdateCartItemView.as_view(),name="update_cart_item",),

    path("items/<int:item_id>/remove/",RemoveCartItemView.as_view(),name="remove_cart_item",),

    path("clear/",ClearCartView.as_view(),name="clear_cart",),
]