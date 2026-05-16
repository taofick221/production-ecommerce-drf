from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import OrderSerializer,CreateOrderSerializer
from .services import create_order
from .selectors import get_user_orders,get_user_orders_by_id
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CreateOrderView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializer=CreateOrderSerializer(data=request.data)
        serializer.is_valid(
            raise_exception=True
        )
        order=create_order(user=request.user,shipping_data=(serializer.validated_data),)
        response_serializer=OrderSerializer(order)
        return Response(response_serializer.data,status=status.HTTP_201_CREATED)
    
class OrderListView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        orders=get_user_orders(request.user)
        serializer=OrderSerializer(orders,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,order_id):
        order=get_object_or_404(get_user_orders(request.user),id=order_id)
        serializer=OrderSerializer(order)
        return Response(serializer.data,status=status.HTTP_200_OK)
        


