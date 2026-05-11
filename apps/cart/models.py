from django.db import models
from decimal import Decimal
from apps.products.models import ProductVariant
from django.conf import settings


class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="cart")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        indexes=[
            models.Index(fields=["user"]),
        ]
    @property
    def subtotal(self):
        total=Decimal(0.00)
        for item in self.items.all():
            total+=item.total_price
        
        return total
    
    @property
    def total(self):
        return self.subtotal
    
    def __str__(self):
        return f"Cart - {self.user.email}"
    

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name="cart_items")
    quantity=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=[
            "cart","variant"
        ]
        indexes=[
            models.Index(fields=["cart"]),
            models.Index(fields=["variant"]),
        ]
    
    @property
    def total_price(self):
        return(self.variant.price*self.quantity)
    
    def __str__(self):
        return (
            f"{self.variant.sku}"
            f" x {self.quantity}"
        )
    