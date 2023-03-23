from django.test import TestCase, Client
from django.urls import reverse
from pst.models import User
from pst.models import DeliveryAddress

class AddAddressViewTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.address_data = {'address': 'Test Address', 'phone_number': '01111111111'}
        self.url = reverse('add_address')

    def test_add_address_with_valid_data(self):
        self.client.login(username='lll@example.org', password='Password123')
        response = self.client.post(reverse('add_address'), data=self.address_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

        addresses = DeliveryAddress.objects.filter(user=self.user)
        self.assertEqual(addresses.count(), 1)
        self.assertEqual(addresses.first().address, self.address_data['address'])
        self.assertEqual(addresses.first().phone_number, '01111111111')

    def test_add_address_with_invalid_data(self):
        self.client.login(username='lll@example.org', password='Password123')
        response = self.client.get(reverse('add_address'))

        self.assertEqual(response.status_code, 200)

        addresses = DeliveryAddress.objects.filter(user=self.user)
        self.assertEqual(addresses.count(), 0)
        self.assertTemplateUsed("index.html")