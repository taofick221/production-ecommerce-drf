from django.db import transaction,IntegrityError
from rest_framework.exceptions import ValidationError
from .models import ProductImage,Product,ProductVariant
from django.utils import timezone

@transaction.atomic
def create_product(validated_data):
    variants_data=validated_data.pop("variants")
    image_data=validated_data.pop("images",[])

    if not variants_data:
        raise ValidationError({
            "variants": "At least one variant required"
        })

    if sum(1 for v in variants_data if v.get("is_default")) !=1:
        raise ValidationError("Exactly one default variant required")
    
    if image_data and sum(1 for img in image_data if img.get("is_primary"))!=1:
        raise ValidationError("Exactly one primary image required")
    
    skus = [
        (v.get("sku") or "").strip().upper()
        for v in variants_data
    ]

    if len(skus) != len(set(skus)):
        raise ValidationError({
            "sku": "Duplicate SKU found"
        })

    combos = [
        (
            (v.get("size") or "").strip().lower(),
            (v.get("color") or "").strip().lower(),
        )
        for v in variants_data
    ]

    if len(combos) != len(set(combos)):
        raise ValidationError({
            "variant": "Duplicate size+color variant"
        })
    
    product=Product.objects.create(**validated_data)

    try:
        for v in variants_data:
            v["size"]=(v.get("size") or "").strip().lower()
            v["color"]=(v.get("color") or "").strip().lower()
            v["sku"]=(v.get("sku") or "").strip().upper()

            variant=ProductVariant(product=product,**v)
            variant.full_clean()
            variant.save()
        
        for img in image_data:
            image=ProductImage(product=product,**img)
            image.full_clean()
            image.save()
    except IntegrityError:
        raise ValidationError({"detail": "Duplicate SKU, variant conflict, or image validation failed"})
    return product

@transaction.atomic
def update_product(instance,validated_data):
    variants_data=validated_data.pop("variants",None)
    image_data=validated_data.pop("images",None)

    for field,value in validated_data.items():
        setattr(instance,field,value)
    instance.save()

    if variants_data is not None:

        if not variants_data:
            raise ValidationError({
                "variants": "At least one variant required"
            })

        existing={v.id:v for v in instance.variants.all()}
        incoming_ids=[]

        if sum(1 for v in variants_data if v.get("is_default"))!=1:
            raise ValidationError("Exactly one default variant required")
        
        skus = [
            (v.get("sku") or "").strip().upper()
            for v in variants_data
        ]

        if len(skus) != len(set(skus)):
            raise ValidationError({
                "sku": "Duplicate SKU found"
            })

        combos = [
            (
                (v.get("size") or "").strip().lower(),
                (v.get("color") or "").strip().lower(),
            )
            for v in variants_data
        ]

        if len(combos) != len(set(combos)):
            raise ValidationError({
                "variant": "Duplicate size+color variant"
            })
        
        for v in variants_data:
            v["size"]=(v.get("size") or "").strip().lower()
            v["color"]=(v.get("color") or "").strip().lower()
            v["sku"]=(v.get("sku") or "").strip().upper()

            v_id=v.get("id")

            if v_id:
                
                variant=existing.get(v_id)
                if not variant:
                    raise ValidationError("Variant not found")
                for field,value in v.items():
                    setattr(variant,field,value)

                variant.full_clean()
                variant.save()
                incoming_ids.append(v_id)
        
            else:
                variant=ProductVariant(product=instance,**v)
                variant.full_clean()
                variant.save()
                incoming_ids.append(variant.id)
        
        for v_id,obj in existing.items():
            if v_id not in incoming_ids:
                obj.delete()
    

    if image_data is not None:
        existing={img.id:img for img in instance.images.all()}
        incoming_ids=[]

        if image_data and sum(1 for img in image_data if img.get("is_primary"))!=1:
            raise ValidationError("Exactly one primary image required")
        
        for img_data in image_data:
            img_id=img_data.get("id")
            if img_id:
                image=existing.get(img_id)
                if not image:
                    raise ValidationError("Image not found")
                
                for field,value in img_data.items():
                    setattr(image,field,value)

                image.full_clean()
                image.save()
                incoming_ids.append(img_id)
            else:
                image=ProductImage(product=instance,**img_data)
                image.full_clean()
                image.save()
                incoming_ids.append(image.id)

        for img_id,obj in existing.items():
            if img_id not in incoming_ids:
                obj.delete()

    return instance



def soft_delete_product(product):
    product.deleted_at=timezone.now()
    product.is_active=False
    product.save(update_fields=["deleted_at","is_active"])