from django.test import TestCase
from pst.models import Reward

class RewardModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Reward.objects.create(name='Test Reward', points_required=100)

    def test_name_label(self):
        reward = Reward.objects.get(id=1)
        field_label = reward._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_points_required_label(self):
        reward = Reward.objects.get(id=1)
        field_label = reward._meta.get_field('points_required').verbose_name
        self.assertEqual(field_label, 'points required')

    def test_default_image(self):
        reward = Reward.objects.get(id=1)
        self.assertEqual(reward.default_image.name, 'rewards/default_reward_image.jpg')

    def test_string_representation(self):
        reward = Reward.objects.get(id=1)
        self.assertEqual(str(reward), 'Test Reward (100 points)')

    def test_image_upload(self):
        reward = Reward.objects.create(name='Test Reward with Image', points_required=200,
                                       image='rewards/test_image.png')
        self.assertEqual(reward.image.name, 'rewards/test_image.png')