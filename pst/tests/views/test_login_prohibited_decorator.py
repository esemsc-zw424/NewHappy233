
from django.test import TestCase
from django.urls import reverse
from pst.models import User


class TestLoginProhibitedDecorator(TestCase):

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.create_user(
            first_name="John", last_name="Example", email='user1@example.com', password="Srx17640408396",
        )
        

    def test_revisit_login_redirect_to_home_page_after_login(self):
        self.client.login(email=self.user.email, password="Srx17640408396")
        response = self.client.get(self.url)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed("home.html")
