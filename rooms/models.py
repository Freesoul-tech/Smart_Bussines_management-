from django.db import models

from businesses.models import Business


class Room(models.Model):

    ROOM_STATUS = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("reserved", "Reserved"),
        ("maintenance", "Maintenance"),
        ("inactive", "Inactive"),
    ]

    ROOM_TYPES = [
        ("single", "Single"),
        ("double", "Double"),
        ("twin", "Twin"),
        ("deluxe", "Deluxe"),
        ("suite", "Suite"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="rooms",
    )

    room_number = models.CharField(
        max_length=20,
    )

    room_type = models.CharField(
        max_length=30,
        choices=ROOM_TYPES,
    )

    floor = models.CharField(
        max_length=30,
        blank=True,
    )

    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=ROOM_STATUS,
        default="available",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["room_number"]
        unique_together = ["business", "room_number"]

    def __str__(self):
        return f"Room {self.room_number}"