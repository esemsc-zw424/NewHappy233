from django.test import TestCase
from pst.forms import PasswordForm

class PasswordFormTest(TestCase):

    def test_passwords_match(self):
        form_data = {
            'password': 'mypassword',
            'new_password': 'Mynewpassword1',
            'password_confirmation': 'Mynewpassword1',
        }
        form = PasswordForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_do_not_match(self):
        form_data = {
            'password': 'mypassword',
            'new_password': 'Mynewpassword1',
            'password_confirmation': 'Mynewpassword2',
        }
        form = PasswordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Confirmation does not match password.', form.errors['password_confirmation'])
