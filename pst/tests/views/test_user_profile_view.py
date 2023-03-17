from django.test import TestCase
from django.urls import reverse
from pst.models import User
from django.test.client import Client


class UserProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='test', last_name='user', email='testuser@test.com', password='testpass')
        self.url = reverse('user_profile')

    def test_user_profile_view_with_authenticated_user(self):
        self.client.login(email='testuser@test.com', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_user_profile_view_with_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)