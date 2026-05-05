from django.db import models,transaction
from django.db.models import UniqueConstraint,Q
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Category(models.Model):
    name=models.CharField(max_length=100,unique=True)
    parent=models.ForeignKey("self",on_delete=models.SET_NULL,related_name="children",blank=True,null=True)

    class Meta:
        indexes=[
            models.Index(fields=["name"]),
            models.Index(fields=["parent"])
        ]

    def __str__(self):
        return self.name


class Brand(models.Model):
    name=models.CharField(max_length=100,unique=True)
    logo=models.ImageField(upload_to="brands/",null=True,blank=True)
    description=models.TextField(blank=True)

    class Meta:
        indexes=[
            models.Index(fields=["name"])
        ]
    def __str__(self):
        return self.name

class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Product(models.Model):
    name=models.CharField(max_length=200)
    slug=models.SlugField(unique=True,blank=True,max_length=200)
    description=models.TextField(blank=True)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    deleted_at=models.DateTimeField(null=True,blank=True)
    is_active=models.BooleanField(default=True)

    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="products")
    brand=models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True,related_name="products")

    objects=ProductManager()
    all_objects=models.Manager()

    class Meta:
        indexes=[
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["category"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["-created_at"]),
        ]
    def save(self,*args, **kwargs):
        if not self.slug:
            base_slug=slugify(self.name)[:200]
            with transaction.atomic():
                slug=base_slug
                counter=1
                while Product.all_objects.filter(slug=slug).exists():
                    slug=f"{base_slug}-{counter}"
                    counter+=1
                self.slug=slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="variants")

    price=models.DecimalField(max_digits=10,decimal_places=2)
    color=models.CharField(max_length=50)
    size=models.CharField(max_length=50)
    stock=models.PositiveIntegerField()
    reserved_stock=models.PositiveIntegerField(default=0)
    sku=models.CharField(max_length=50,unique=True)
    is_default=models.BooleanField(default=False)

    class Meta:
        indexes=[
            models.Index(fields=["product"]),
            models.Index(fields=["sku"])
        ]

        constraints=[
            UniqueConstraint(fields=["product","color","size"],name="unique_variant"),
            UniqueConstraint(fields=["product"],condition=Q(is_default=True),name="unique_default_variant_per_product"),
            
        ]
    def clean(self):
        if self.price<=0:
            raise ValidationError("Price must be positive")
        if self.reserved_stock>self.stock:
            raise ValidationError("Rerserved stock cannot exceed stock")
    
    def save(self,*args, **kwargs):
        if self.is_default:
            ProductVariant.objects.filter(
                product=self.product,
                is_default=True,
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def available_stock(self):
        return self.stock-self.reserved_stock



    def __str__(self):
        return f"{self.product}-{self.size}-{self.color}"
    


class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")
    image=models.ImageField(upload_to="products/",null=True,blank=True)
    alt_text=models.CharField(max_length=100,blank=True)
    order=models.PositiveIntegerField(default=0)
    is_primary=models.BooleanField(default=False)

    class Meta:
        ordering=["order"]
        indexes=[
            models.Index(fields=["product"]),
        ]
        constraints=[
            UniqueConstraint(fields=["product"],condition=Q(is_primary=True),name="unique_primary_image_per_product")
        ]
    def __str__(self):
        return f"{self.product.name} Image"

























