from django.contrib import admin

from .models import ParkingSpace, Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("registration_number", "business", "vehicle_type", "customer", "is_checked_in")
    list_filter = ("vehicle_type", "is_checked_in")
    search_fields = ("registration_number", "customer__name")


@admin.register(ParkingSpace)
class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ("space_number", "business", "status", "current_vehicle")
    list_filter = ("status",)
    search_fields = ("space_number", "current_vehicle__registration_number")
