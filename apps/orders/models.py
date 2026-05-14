from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.products.models import ProductVariant

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING="pending","Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
    
    class PaymentStatus(models.TextChoices):
        PENDING="pending","Pending"
        PAID="paid","Paid"
        FAILED="failed","Failed"
        REFUNDED="refunded","Refunded"
    
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="orders",)
    order_number=models.CharField(max_length=50,unique=True)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    payment_status=models.CharField(max_length=20,choices=PaymentStatus.choices,default=PaymentStatus.PENDING)
    subtotal=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal("0.00"))
    total=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal("0.00"))
    full_name=models.CharField(max_length=100)
    phone=models.CharField(max_length=20)
    address=models.TextField()
    city=models.CharField(max_length=100)
    postal_code=models.CharField(max_length=20)
    paid_at=models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=["-created_at"]
        indexes=[
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["-created_at"]),
        ]
    
    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    variant=models.ForeignKey(ProductVariant,on_delete=models.PROTECT,related_name="order_items")
    product_name=models.CharField(max_length=250)
    sku=models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2,)
    size=models.CharField(max_length=50)
    color=models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10,decimal_places=2,)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["variant"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return (
            f"{self.product_name}"
            f" x {self.quantity}"
        )
    