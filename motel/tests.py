from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from businesses.models import Business
from rooms.models import Room

from .models import ParkingSpace, Vehicle


class MotelIsolationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="motel-owner", password="password")
        self.other_user = user_model.objects.create_user(username="hotel-owner", password="password")
        self.business = Business.objects.create(owner=self.user, name="Roadside Motel", business_model="motel")
        self.other_business = Business.objects.create(owner=self.other_user, name="City Hotel", business_model="hotel")
        Room.objects.create(business=self.business, room_number="1", room_type="single", price_per_night=50)
        Room.objects.create(business=self.other_business, room_number="1", room_type="single", price_per_night=100)

    def test_dashboard_only_shows_current_business_counts(self):
        Vehicle.objects.create(business=self.business, registration_number="MOT-001")
        Vehicle.objects.create(business=self.other_business, registration_number="HOT-001")
        self.client.login(username="motel-owner", password="password")
        response = self.client.get(reverse("motel:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["vehicles_checked_in"], 0)
        self.assertContains(response, "Roadside Motel")
        self.assertNotContains(response, "HOT-001")

    def test_hotel_owner_cannot_open_motel_dashboard(self):
        self.client.login(username="hotel-owner", password="password")
        response = self.client.get(reverse("motel:dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_vehicle_check_in_assigns_only_a_business_parking_space(self):
        vehicle = Vehicle.objects.create(business=self.business, registration_number="MOT-002")
        space = ParkingSpace.objects.create(business=self.business, space_number="A1")
        other_space = ParkingSpace.objects.create(business=self.other_business, space_number="A1")
        self.client.login(username="motel-owner", password="password")

        response = self.client.post(
            reverse("motel:vehicle_check_in", args=[vehicle.id]),
            {"parking_space": space.id},
        )

        self.assertRedirects(response, reverse("motel:vehicles"))
        vehicle.refresh_from_db()
        space.refresh_from_db()
        other_space.refresh_from_db()
        self.assertTrue(vehicle.is_checked_in)
        self.assertEqual(space.current_vehicle_id, vehicle.id)
        self.assertIsNone(other_space.current_vehicle_id)
