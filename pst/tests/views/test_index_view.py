from django.test import TestCase
from django.test import Client
from django.urls import reverse
from pst.models import User
from pst.models import Reward, DeliveryAddress


class IndexViewTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.address = DeliveryAddress.objects.create(
            user=self.user, address='123 Test St', phone_number='12345')
        self.reward1 = Reward.objects.create(
            name='T-shirt', points_required=10, image='rewards/shirt.jpg')
        self.reward2 = Reward.objects.create(
            name='PSN £50 Gift Card', points_required=500, image='rewards/playstation_gift_card.jpg')
        self.client.login(username='testuser', password='testpass')

    def test_index_view_with_no_rewards(self):
        self.client.login(username='lll@example.org', password='Password123')
        Reward.objects.all().delete()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task_points'], 0)

    def test_index_view_with_rewards(self):
        self.client.login(username='lll@example.org', password='Password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task_points'], 0)

    def test_index_view_with_address(self):
        self.client.login(username='lll@example.org', password='Password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['address'], self.address)

    def test_index_view_with_no_address(self):
        self.client.login(username='lll@example.org', password='Password123')
        self.address.delete()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['address'])

    def test_index_view_with_form_instance(self):
        self.client.login(username='lll@example.org', password='Password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, self.address)

    def test_index_view_creates_rewards_if_none_exist(self):
        self.client.login(username='lll@example.org', password='Password123')
        Reward.objects.all().delete()
        self.assertEqual(Reward.objects.count(), 0)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reward.objects.count(), 4)