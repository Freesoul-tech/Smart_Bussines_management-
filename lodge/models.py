from django.db import models

from businesses.models import Business
from reservations.models import Reservation
from rooms.models import Room


class LodgeUnit(models.Model):
    UNIT_TYPES = [
        ("cabin", "Cabin"),
        ("chalet", "Chalet"),
        ("lodge_room", "Lodge Room"),
        ("family_unit", "Family Unit"),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="lodge_units")
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name="lodge_unit")
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES, default="lodge_room")
    view_description = models.CharField(max_length=255, blank=True)
    max_guests = models.PositiveIntegerField(default=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["room__room_number"]

    def __str__(self):
        return f"{self.get_unit_type_display()} {self.room.room_number}"


class LodgeActivity(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="lodge_activities")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["business", "name"], name="unique_lodge_activity_name"),
        ]

    def __str__(self):
        return self.name


class LodgePackage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="lodge_packages")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    included_activities = models.ManyToManyField(LodgeActivity, blank=True, related_name="packages")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["business", "name"], name="unique_lodge_package_name"),
        ]

    def __str__(self):
        return self.name


class PackageBooking(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="lodge_package_bookings")
    package = models.ForeignKey(LodgePackage, on_delete=models.PROTECT, related_name="bookings")
    quantity = models.PositiveIntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["reservation", "package"], name="unique_lodge_package_booking"),
        ]

    @property
    def total_amount(self):
        return self.package.price * self.quantity
