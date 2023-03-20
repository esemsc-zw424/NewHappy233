from django.test import TestCase
from django.urls import reverse
from pst.models import User
from pst.models import Reward

class RedeemTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')

        self.reward = Reward.objects.create(
            name='T-shirt', points_required=20, image='rewards/shirt.jpg')

    def test_redeem_with_enough_points(self):
        self.client.login(email='lll@example.org', password='Password123')
        self.user.total_task_points = 100
        self.user.save()
        response = self.client.get(reverse('redeem', args=[self.reward.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.total_task_points, 100)

    def test_redeem_insufficient_points(self):
        self.client.login(email='lll@example.org', password='Password123')
        self.user.total_task_points = 10
        self.user.save()
        response = self.client.get(reverse('redeem', args=[self.reward.id]))
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(self.user.total_task_points, 10)

    def test_redeem_with_no_points(self):
        self.client.login(email='lll@example.org', password='Password123')
        response = self.client.get(reverse('redeem', args=[self.reward.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.total_task_points, 0)

    def test_redeem_unauthenticated_user(self):
        response = self.client.get(reverse('redeem', args=[self.reward.id]))
        self.assertRedirects(response, '/accounts/login/?next=/redeem/%s/' % self.reward.id)