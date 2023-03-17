from pst.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse

class UserGuidelineViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(first_name='John', last_name='Tester', email='testuser@example.com',
                                             password='testpass')

    def test_user_guideline_view_with_authenticated_user(self):
        # Log in the user
        self.client.login(email='testuser@example.com', password='testpass')

        # Create a GET request to the user_guideline view
        url = reverse('user_guideline')
        response = self.client.get(url)

        # Check that the response has a 200 status code
        self.assertEqual(response.status_code, 200)

        # Check that the 'user_guideline.html' template is used
        self.assertTemplateUsed(response, 'user_guideline.html')

    def test_user_guideline_view_with_unauthenticated_user(self):
        # Create a GET request to the user_guideline view
        url = reverse('user_guideline')
        response = self.client.get(url)

        # Check that the response has a 302 status code (redirect to login page)
        self.assertEqual(response.status_code, 302)

        # Check that the 'login' page is the target of the redirect
        self.assertRedirects(response, '/accounts/login/?next=' + url)