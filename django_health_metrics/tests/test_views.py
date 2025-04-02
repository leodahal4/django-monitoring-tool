from django.test import TestCase, Client
from django.urls import reverse

class HealthViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_view(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('memory', response.json())