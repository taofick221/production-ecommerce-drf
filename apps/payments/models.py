from decimal import Decimal

from django.db import models

from apps.orders.models import Order


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class Provider(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        SSLCOMMERZ = "sslcommerz", "SSLCOMMERZ"
        CASH_ON_DELIVERY = "cod", "Cash On Delivery"

    # one order = one payment
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    # payment gateway/provider
    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
    )

    # payment transaction status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # unique transaction id
    transaction_id = models.CharField(
        max_length=255,
        unique=True,
    )

    # payment amount snapshot
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # successful payment time
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["provider"]),
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.transaction_id