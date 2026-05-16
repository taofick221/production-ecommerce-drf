from django.urls import path

from .views import (
    CreateOrderView,
    OrderListView,
    OrderDetailView,
)

urlpatterns = [
    path("create/",CreateOrderView.as_view(),name="create_order",),
    path("",OrderListView.as_view(),name="orders",),
    path("<int:order_id>/",OrderDetailView.as_view(),name="order_detail",),
]