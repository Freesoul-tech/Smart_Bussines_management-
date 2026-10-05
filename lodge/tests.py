from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from businesses.models import Business
from rooms.models import Room

from .models import LodgeActivity, LodgePackage, LodgeUnit


class LodgeTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="lodge-owner", password="password")
        self.other_user = user_model.objects.create_user(username="hotel-owner", password="password")
        self.business = Business.objects.create(owner=self.user, name="Forest Lodge", business_model="lodge")
        self.other_business = Business.objects.create(owner=self.other_user, name="City Hotel", business_model="hotel")
        room = Room.objects.create(business=self.business, room_number="C1", room_type="single", price_per_night=80)
        LodgeUnit.objects.create(business=self.business, room=room, unit_type="cabin", max_guests=4)

    def test_dashboard_is_lodge_only_and_counts_units(self):
        self.client.login(username="lodge-owner", password="password")
        response = self.client.get(reverse("lodge:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_units"], 1)
        self.assertEqual(response.context["cabins"], 1)
        self.assertContains(response, "Forest Lodge")

    def test_hotel_owner_cannot_open_lodge_dashboard(self):
        self.client.login(username="hotel-owner", password="password")
        self.assertEqual(self.client.get(reverse("lodge:dashboard")).status_code, 403)

    def test_package_activity_relationship_is_business_scoped(self):
        activity = LodgeActivity.objects.create(business=self.business, name="Guided walk", price=15)
        package = LodgePackage.objects.create(business=self.business, name="Forest weekend", price=120)
        package.included_activities.add(activity)
        self.assertEqual(package.included_activities.get().business_id, self.business.id)
