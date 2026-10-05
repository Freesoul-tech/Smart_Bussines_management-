
from decimal import Decimal
from django.db import models

from businesses.models import Business
from rooms.models import Room


class Reservation(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("checked_in", "Checked In"),
        ("checked_out", "Checked Out"),
        ("cancelled", "Cancelled"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="reservations",
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservations",
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reservations",
    )

    customer_name = models.CharField(
        max_length=200,
    )

    customer_phone = models.CharField(
        max_length=30,
        blank=True,
    )

    customer_email = models.EmailField(
        blank=True,
    )

    check_in = models.DateField()

    check_out = models.DateField()

    number_of_guests = models.PositiveIntegerField(
        default=1,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
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
        ordering = ["-check_in", "-created_at"]

    @property
    def total_nights(self):

        if not self.check_in or not self.check_out:
            return 0

        return max(
            (self.check_out - self.check_in).days,
            0,
        )

    @property
    def total_amount(self):

        if not self.room:
            return Decimal("0.00")

        return (
            self.room.price_per_night
            * self.total_nights
        )

    @property
    def total_paid(self):

        return sum(
            (
                payment.amount
                for payment in self.payments.all()
                if payment.status == "paid"
            ),
            Decimal("0.00"),
        )

    @property
    def balance(self):
        """
        Remaining amount owed
        on the reservation.
        """

        balance = (
            self.total_amount
            - self.total_paid
        )

        return max(
            balance,
            Decimal("0.00"),
        )

    @property
    def is_paid_in_full(self):

        return (
            self.total_amount > Decimal("0.00")
            and self.balance <= Decimal("0.00")
        )

    def __str__(self):

        return (
            f"{self.customer_name} - "
            f"Room {self.room.room_number} - "
            f"{self.check_in} to {self.check_out}"
        )

