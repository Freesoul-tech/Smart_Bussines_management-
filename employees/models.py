from django.conf import settings
from django.db import models

from businesses.models import Business


class Employee(models.Model):

    EMPLOYMENT_STATUS = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="employees",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profiles",
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    position = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS,
        default="active",
    )

    date_joined = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"