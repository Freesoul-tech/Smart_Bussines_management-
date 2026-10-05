from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "position",
        "business",
        "employment_status",
        "phone",
        "date_joined",
    )

    list_filter = (
        "employment_status",
        "business",
    )

    search_fields = (
        "first_name",
        "last_name",
        "position",
        "phone",
        "email",
    )

    ordering = (
        "first_name",
        "last_name",
    )
    