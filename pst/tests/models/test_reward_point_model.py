from django.test import TestCase
from pst.models import User
from pst.models import RewardPoint

class RewardPointModelTest(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email = 'lll@example.org')
        self.reward_point = RewardPoint.objects.create(
            user=self.user, points=100
        )

    def test_reward_point_str(self):
        self.assertEqual(str(self.reward_point), 'None: 100 points')

    def test_reward_point_user(self):
        self.assertEqual(self.reward_point.user, self.user)

    def test_reward_point_points(self):
        self.assertEqual(self.reward_point.points, 100)