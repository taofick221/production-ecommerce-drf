# apps/cart/views.py

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CartItem

from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)

from .services import (
    get_or_create_cart,
    add_to_cart,
    update_cart_item,
    remove_cart_item,
    clear_cart,
)

from .selectors import get_user_cart


# ---------- CART ----------
class CartView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        get_or_create_cart(request.user)

        cart = get_user_cart(request.user)

        serializer = CartSerializer(cart)

        return Response(serializer.data)


# ---------- ADD ----------
class AddToCartView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AddToCartSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        cart = add_to_cart(
            user=request.user,
            variant=serializer.validated_data["variant"],
            quantity=serializer.validated_data["quantity"],
        )

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED,
        )


# ---------- UPDATE ----------
class UpdateCartItemView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):

        cart_item = get_object_or_404(
            CartItem.objects.select_related(
                "cart",
                "variant",
            ),
            id=item_id,
            cart__user=request.user,
        )

        serializer = UpdateCartItemSerializer(
            data=request.data,
            context={
                "cart_item": cart_item
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        update_cart_item(
            cart_item=cart_item,
            quantity=serializer.validated_data["quantity"],
        )

        return Response(
            CartSerializer(
                cart_item.cart
            ).data
        )


# ---------- REMOVE ----------
class RemoveCartItemView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):

        cart_item = get_object_or_404(
            CartItem.objects.select_related(
                "cart"
            ),
            id=item_id,
            cart__user=request.user,
        )

        cart = cart_item.cart

        remove_cart_item(cart_item)

        return Response(
            CartSerializer(cart).data
        )


# ---------- CLEAR ----------
class ClearCartView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        cart = get_or_create_cart(
            request.user
        )

        clear_cart(cart)

        return Response(
            CartSerializer(cart).data
        )
    










