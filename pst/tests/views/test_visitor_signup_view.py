from django.test import TestCase
from django.urls import reverse
from pst.forms import VisitorSignupForm
from pst.models import User


class VisitorSignupViewTestCase(TestCase):

    fixtures = [
        'pst/tests/fixtures/users.json'
    ]

    def setUp(self):
        self.url = reverse('visitor_signup')
        self.form_input = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.org',
        'password': 'Password123',
        'confirm_password': 'Password123'
    }

    def test_visitor_signup_url(self):
        self.assertEqual(self.url, '/visitor_signup/')

    def test_get_signup_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitor_signup.html')
        form = response.context['form']
        self.assertTrue(form, VisitorSignupForm)
        self.assertFalse(form.is_bound)

    def test_successful_signup(self):
        #User.objects.filter(email=self.form_input['email']).delete()
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(before_count + 1, after_count)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTrue(self._is_logged_in())
        user = User.objects.get(email='johndoe@example.org')
        self.assertEqual(user.first_name, 'john')
        self.assertEqual(user.last_name, 'doe')
        self.assertEqual(user.email, 'johndoe@example.org')
        # is_password_correct = check_password('Password123', user.password)
        # self.assertTrue(is_password_correct)

    def test_unsuccessful_signup(self):
        self.form_input['email'] = 'BAD'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitor_signup.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, VisitorSignupForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()