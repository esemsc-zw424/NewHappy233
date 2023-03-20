from django.test import TestCase
from django.urls import reverse
from pst.forms import EditProfileForm
from pst.models import User

class ProfileViewTest(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')
        self.url = reverse('edit_profile')
        self.form_input = {
            'first_name': 'John',
            'last_name': 'Doe',
            'bio': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'gender': 'Male',
            'phone_number': '1234567890',
            'address': '123 Main St.'
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/edit_profile/')

    def test_get_profile(self):
        self.client.login(email='lll@example.org', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertEqual(form.instance, self.user)

    def test_profile_update_result(self):
        self.client.login(email='lll@example.org', password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('home')
        self.assertTemplateUsed(response, 'user_profile.html')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')