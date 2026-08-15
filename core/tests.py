from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import PricingConfig, ScaifeEntry, Office, Inquiry, BrandingSettings
from decimal import Decimal

class PublicPagesTest(TestCase):
    def test_public_pages_load(self):
        """
        Verify that all public website routes load successfully.
        Home now redirects to login, so we check for 302 redirect for it,
        and 200 for all other public pages.
        """
        pages = ['about', 'services', 'gallery', 'faqs', 'terms', 'privacy', 'login']
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200, f"Page {page} failed to load.")
        # Home should redirect to login when unauthenticated
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302, "Home should redirect unauthenticated users to login.")


class CoreModelsTest(TestCase):
    def setUp(self):
        # Create singleton setup
        self.pricing = PricingConfig.get_solo()
        self.pricing.lapping_rate = Decimal('150.00')
        self.pricing.coating_rate = Decimal('200.00')
        self.pricing.save()

        self.office = Office.objects.create(
            name="Surat Test Office",
            location="Test Location, Surat",
            phone="12345",
            email="test@test.com"
        )

        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_scaife_cost_calculation(self):
        """
        Verify cost auto-calculation logic for Scaife entries.
        Cost = quantity * (sum of selected service rates)
        """
        entry = ScaifeEntry.objects.create(
            client_name="Test Client",
            quantity=3,
            service_lapping=True,
            service_coating=True,
            service_diamond_scaife=False,
            assigned_office=self.office,
            created_by=self.user
        )

        # Expected cost = 3 * (150 + 200) = 3 * 350 = 1050.00
        self.assertEqual(entry.cost, Decimal('1050.00'))

    def test_contact_inquiry_submission(self):
        """
        Verify that contact form submission creates Inquiry record.
        """
        response = self.client.post(reverse('contact'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'subject': 'Lapping Quote',
            'message': 'Please quote for 10 plates.'
        })
        self.assertEqual(response.status_code, 302)  # Redirects on success
        inquiries = Inquiry.objects.filter(email='john@example.com')
        self.assertEqual(inquiries.count(), 1)
        self.assertEqual(inquiries.first().subject, 'Lapping Quote')

    def test_settings_page_load(self):
        """
        Verify that admin settings page loads cleanly without ValueError on strftime.
        """
        admin_user = User.objects.create_superuser(username="admin_test", email="admin@test.com", password="password123")
        admin_user.profile.role = 'admin'
        admin_user.profile.save()
        self.client.login(username="admin_test", password="password123")
        response = self.client.get(reverse('settings_edit'))
        self.assertEqual(response.status_code, 200, "Settings page failed to load.")
