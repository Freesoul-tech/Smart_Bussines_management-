from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from businesses.models import Business


class DashboardNavigationTests(TestCase):

	def test_bakery_dashboard_uses_shared_payments(self):
		user = get_user_model().objects.create_user(
			username="bakery-owner",
			password="test-password",
		)
		Business.objects.create(
			owner=user,
			name="Test Bakery",
			business_model="bakery",
		)
		self.client.force_login(user)

		response = self.client.get(reverse("dashboard:dashboard"))

		self.assertContains(response, 'href="/payments/"')
		self.assertNotContains(response, "/business/restaurant/payments/")
		self.assertEqual(self.client.get(reverse("payment_list")).status_code, 200)

		for route_name in [
			"bakery:dashboard",
			"bakery:products",
			"bakery:ingredients",
			"bakery:recipes",
			"bakery:production",
			"bakery:orders",
			"bakery:suppliers",
			"bakery:expenses",
			"bakery:inventory",
			"bakery:reports",
		]:
			self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)
