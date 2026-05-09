from .models import  Product

def get_products():
    return(
        Product.objects.select_related("category","brand").prefetch_related("variants","images").
        filter(deleted_at__isnull=True,is_active=True).order_by("-created_at")

    )