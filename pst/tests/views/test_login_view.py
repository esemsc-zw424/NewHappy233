from django.test import TestCase
from django.urls import reverse
from pst.tests.helpers import LogInTester, reverse_with_next
from pst.models import User
from pst.forms import LoginForm




class LogInViewTestCase(TestCase, LogInTester):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(email = 'lll@example.org')
        


    def test_login_url(self):
        self.assertEqual(self.url, "/log_in/")


    def test_get_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(form.is_bound)
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 0)

    def test_get_login_with_redirect(self):
        # test when login required decorator is used
        destination_url = reverse('home')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        #next = response.context['next']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(form.is_bound)
        #self.assertEqual(next, destination_url)
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 0)

    def test_get_login_redirects_when_logged_in(self):
        self.client.login(email='lll@example.org', password='Password123') 
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_successful_log_in(self):
        form_input = { 'email': 'lll@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 0)



    def test_unsuccessful_log_in(self):
        form_input = { 'email': 'wwwwww', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_email(self):
        form_input = { 'email': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = { 'email': 'lll@example.org', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)

    

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = { 'email': 'lll@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)

