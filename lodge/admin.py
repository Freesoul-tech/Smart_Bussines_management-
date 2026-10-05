from django.contrib import admin

from .models import LodgeActivity, LodgePackage, LodgeUnit, PackageBooking


@admin.register(LodgeUnit)
class LodgeUnitAdmin(admin.ModelAdmin):
    list_display = ("room", "business", "unit_type", "max_guests", "is_active")
    list_filter = ("unit_type", "is_active")


@admin.register(LodgeActivity)
class LodgeActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "price", "is_active")
    list_filter = ("is_active",)


@admin.register(LodgePackage)
class LodgePackageAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "price", "is_active")
    list_filter = ("is_active",)


@admin.register(PackageBooking)
class PackageBookingAdmin(admin.ModelAdmin):
    list_display = ("reservation", "package", "quantity", "booked_at")
