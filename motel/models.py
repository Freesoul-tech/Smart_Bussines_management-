from django.db import models

from businesses.models import Business
from customers.models import Customer
from reservations.models import Reservation


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ("car", "Car"),
        ("motorcycle", "Motorcycle"),
        ("van", "Van"),
        ("truck", "Truck"),
        ("other", "Other"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="motel_vehicles",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="motel_vehicles",
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
    )
    registration_number = models.CharField(max_length=30)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default="car")
    description = models.CharField(max_length=255, blank=True)
    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["registration_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "registration_number"],
                name="unique_motel_vehicle_registration",
            ),
        ]

    def __str__(self):
        return self.registration_number


class ParkingSpace(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("maintenance", "Maintenance"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="parking_spaces",
    )
    space_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    current_vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parking_space",
    )
    assigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["space_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "space_number"],
                name="unique_motel_parking_space",
            ),
        ]

    @property
    def is_occupied(self):
        return self.current_vehicle_id is not None

    def __str__(self):
        return f"Space {self.space_number}"
