from django.db import models
from businesses.models import Business


class BusinessSettings(models.Model):
    """
    Stores configurable preferences for a business.
    Core business information remains in the Business model.
    """

    TIME_FORMAT_CHOICES = [
        ("12", "12-hour"),
        ("24", "24-hour"),
    ]

    THEME_CHOICES = [
        ("system", "System Default"),
        ("light", "Light"),
        ("dark", "Dark"),
    ]

    LANGUAGE_CHOICES = [
        ("en", "English"),
    ]

    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    currency = models.CharField(
        max_length=10,
        default="MWK",
    )

    date_format = models.CharField(
        max_length=30,
        default="DD/MM/YYYY",
    )

    time_format = models.CharField(
        max_length=2,
        choices=TIME_FORMAT_CHOICES,
        default="24",
    )

    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="en",
    )

    email_notifications = models.BooleanField(
        default=True,
    )

    low_stock_alerts = models.BooleanField(
        default=True,
    )

    sales_notifications = models.BooleanField(
        default=True,
    )

    payment_notifications = models.BooleanField(
        default=True,
    )

    report_notifications = models.BooleanField(
        default=True,
    )

    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default="system",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        permissions = [
            ("view_reports", "Can view business reports"),
        ]

    def __str__(self):
        return f"Settings - {self.business.name}"