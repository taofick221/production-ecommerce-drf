import django_filters as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    category=filters.NumberFilter(
        field_name="category_id"
    )
    brand=filters.NumberFilter(
        field_name="brand_id"
    )
    size=filters.CharFilter(
        field_name="variants__size",
        lookup_expr="iexact"
    )
    color=filters.CharFilter(
        field_name="variants__color",
        lookup_expr="iexact"
    )
    min_price=filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="gte"
    )
    max_price=filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="lte"
    )
    class Meta:
        model=Product
        fields=[]