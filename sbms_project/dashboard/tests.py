from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='secret123')
        self.client.force_login(self.user)
    def test_hotel_business_shows_core_modules(self):
        session = self.client.session
        session['selected_business_type'] = 'hotel'
        session['business_profile'] = {
            'business_type': 'hotel',
            'business_name': 'Hotel One',
            'business_location': 'Lilongwe, Malawi',
            'business_email': 'info@hotelone.mw',
            'business_requirements': 'Need reservations',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Authentication &amp; Role Management')
        self.assertContains(response, 'Customers')
        self.assertContains(response, 'Inventory')
        self.assertContains(response, 'Sales/ Sales and Point of Sale (POS)')
        self.assertContains(response, 'Reports &amp; Analytics')

    def test_restaurant_business_shows_core_modules(self):
        session = self.client.session
        session['selected_business_type'] = 'restaurant'
        session['business_profile'] = {
            'business_type': 'restaurant',
            'business_name': 'Taste House',
            'business_location': 'Blantyre, Malawi',
            'business_email': 'hello@tastehouse.mw',
            'business_requirements': 'Need inventory',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Authentication &amp; Role Management')
        self.assertContains(response, 'Procurement')
        self.assertContains(response, 'Expenses')
        self.assertContains(response, 'Notifications')
        self.assertContains(response, 'Settings')

    def test_dashboard_marks_selected_business_as_active(self):
        session = self.client.session
        session['selected_business_type'] = 'hotel'
        session['business_profile'] = {
            'business_type': 'hotel',
            'business_name': 'Hotel One',
            'business_location': 'Lilongwe, Malawi',
            'business_email': 'info@hotelone.mw',
            'business_requirements': 'Need reservations',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="hotel" class="sidebar-btn active"')
        self.assertContains(response, 'aria-current="page"')

    def test_restaurant_business_shows_tailored_modules_and_headline(self):
        session = self.client.session
        session['selected_business_type'] = 'restaurant'
        session['business_profile'] = {
            'business_type': 'restaurant',
            'business_name': 'Taste House',
            'business_location': 'Blantyre, Malawi',
            'business_email': 'hello@tastehouse.mw',
            'business_requirements': 'Need inventory',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Restaurant Business')
        self.assertContains(response, 'Kitchen Operations')
        self.assertContains(response, 'Table Management')

    def test_business_type_menu_renders_as_links(self):
        session = self.client.session
        session['selected_business_type'] = 'hotel'
        session['business_profile'] = {
            'business_type': 'hotel',
            'business_name': 'Hotel One',
            'business_location': 'Lilongwe, Malawi',
            'business_email': 'info@hotelone.mw',
            'business_requirements': 'Need reservations',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/?business_type=hotel"')
        self.assertContains(response, 'href="/?business_type=restaurant"')
        self.assertContains(response, 'href="/?business_type=guest%20house"')

    def test_dashboard_includes_report_and_export_actions(self):
        session = self.client.session
        session['selected_business_type'] = 'hotel'
        session['business_profile'] = {
            'business_type': 'hotel',
            'business_name': 'Hotel One',
            'business_location': 'Lilongwe, Malawi',
            'business_email': 'info@hotelone.mw',
            'business_requirements': 'Need reservations',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generate Report')
        self.assertContains(response, 'Export to Excel')
        self.assertContains(response, 'Export to PDF')

    def test_selected_modules_render_as_direct_links(self):
        session = self.client.session
        session['selected_business_type'] = 'guest house'
        session['business_profile'] = {
            'business_type': 'guest house',
            'business_name': 'Lakeview Guest House',
            'business_location': 'Zomba, Malawi',
            'business_email': 'stay@lakeviewmw.com',
            'business_requirements': 'Need guest management',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/guests/"')
        self.assertContains(response, 'href="/reservations/"')
        self.assertContains(response, 'href="/housekeeping/"')
        self.assertContains(response, 'href="/billing/"')
        self.assertContains(response, 'href="/reports-analytics/"')
        self.assertContains(response, 'href="/notifications/"')
        self.assertContains(response, 'href="/settings/"')

    def test_user_must_select_business_model_after_login(self):
        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a business model')
        self.assertContains(response, 'Hotel')
        self.assertContains(response, 'Motel')
        self.assertContains(response, 'Restaurant')
        self.assertContains(response, 'Boutique')

    def test_selected_business_model_persists_for_future_visits(self):
        session = self.client.session
        session['selected_business_type'] = 'restaurant'
        session['business_profile'] = {
            'business_type': 'restaurant',
            'business_name': 'Sunrise Grill',
            'business_location': 'Blantyre, Malawi',
            'business_email': 'hello@sunrisegrill.mw',
            'business_requirements': 'Need POS and inventory tracking',
        }
        session.save()

        response = self.client.get(reverse('dashboard:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Restaurant Business')
        self.assertContains(response, 'Kitchen Operations')

    def test_business_profile_onboarding_is_required_before_dashboard_access(self):
        response = self.client.get(reverse('dashboard:index'), {'business_type': 'restaurant'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tell us about your business')
        self.assertContains(response, 'Business name')
        self.assertContains(response, 'Business location / address')
        self.assertContains(response, 'Business email')

        response = self.client.post(
            reverse('dashboard:index'),
            {
                'business_type': 'restaurant',
                'business_name': 'Sunrise Grill',
                'business_location': 'Blantyre, Malawi',
                'business_email': 'hello@sunrisegrill.mw',
                'business_requirements': 'Need POS and inventory tracking',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Restaurant Business')
        self.assertContains(response, 'Sunrise Grill')

    def test_login_page_has_professional_white_branding(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard:login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart Business Management Suite')
        self.assertContains(response, 'Log in')
        self.assertContains(response, 'Create account')

    def test_user_can_register_from_auth_page(self):
        self.client.logout()
        response = self.client.post(
            reverse('dashboard:register'),
            {
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'username': 'newuser',
                'password1': 'StrongPass123',
                'password2': 'StrongPass123',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())
        self.assertContains(response, 'Select a business model')
        self.assertContains(response, 'Hotel')
        self.assertContains(response, 'Restaurant')
        self.assertContains(response, 'Boutique')

    def test_user_can_delete_their_account_from_settings(self):
        response = self.client.post(
            reverse('dashboard:delete_account'),
            {'confirm': 'DELETE'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(pk=self.user.pk).exists())
        self.assertContains(response, 'Log in')
