from django.db import models

from businesses.models import Business
from businesses.models import Order
from businesses.models import Reservation as RestaurantReservation
from reservations.models import Reservation


class Payment(models.Model):

    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile_money", "Mobile Money"),
        ("bank_transfer", "Bank Transfer"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payments",
    )

    restaurant_order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payments",
    )

    restaurant_reservation = models.ForeignKey(
        RestaurantReservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )

    bakery_order = models.ForeignKey(
        "businesses.BakeryOrder",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payments",
    )

    pub_bar_order = models.ForeignKey(
        "businesses.PubBarOrder",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payments",
    )

    boutique_order = models.ForeignKey(
        "businesses.BoutiqueOrder",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHODS,
        default="cash",
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="paid",
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.pub_bar_order_id:
            return f"Pub/Bar Order #{self.pub_bar_order_id} - {self.amount}"
        if self.bakery_order_id:
            return f"Bakery Order #{self.bakery_order_id} - {self.amount}"
        if self.boutique_order_id:
            return f"Boutique Sale #{self.boutique_order_id} - {self.amount}"
        if self.restaurant_order_id:
            return f"Order #{self.restaurant_order_id} - {self.amount}"
        return (
            f"{self.reservation.customer_name} - "
            f"{self.amount}"
        )