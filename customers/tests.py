from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from businesses.models import Business

# Create your tests here.


class CustomerAddTests(TestCase):
	def setUp(self):
		user = get_user_model().objects.create_user(
			username="customer-owner",
			password="password",
		)
		Business.objects.create(
			owner=user,
			name="Roadside Motel",
			business_model="motel",
		)
		self.client.login(username="customer-owner", password="password")

	def test_add_page_renders_without_detail_url_error(self):
		response = self.client.get(reverse("customers:customer_add"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'href="/customers/"')

	def test_add_redirects_to_saved_customer_detail(self):
		response = self.client.post(
			reverse("customers:customer_add"),
			{"name": "A Guest", "phone": "555-0100"},
		)

		customer = Business.objects.get(name="Roadside Motel").customers.get()
		self.assertRedirects(
			response,
			reverse("customers:customer_detail", args=[customer.id]),
		)
