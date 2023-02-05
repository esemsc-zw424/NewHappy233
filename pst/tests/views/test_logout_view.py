from django.test import TestCase
from django.urls import reverse
from pst.tests.helpers import LogInTester
from pst.models import User

class LogOutViewTestCase(TestCase, LogInTester):
    fixtures = ['pst/tests/fixtures/users.json']


    def setUp(self):
        self.url = reverse('log_out')

    def test_logout_url(self):
        self.assertEqual(self.url, '/log_out/')


    def test_get_log_out(self):
        self.client.login(email='lll@example.org', password='Password123') 
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('visitor_introduction')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'visitor_introduction.html')
        self.assertFalse(self._is_logged_in())

    def test_get_log_out_without_being_logged_in(self):
        response = self.client.get(self.url, follow=True)
        response_url = reverse('visitor_introduction')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'visitor_introduction.html')
        self.assertFalse(self._is_logged_in())
