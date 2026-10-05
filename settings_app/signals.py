from django.db.models.signals import post_save
from django.dispatch import receiver

from businesses.models import Business
from .models import BusinessSettings


@receiver(post_save, sender=Business)
def create_business_settings(sender, instance, created, **kwargs):
    if created:
        BusinessSettings.objects.get_or_create(
            business=instance
        )