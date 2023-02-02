from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from pst.forms import VisitorSignupForm
from pst.models import User
from django.urls import reverse

class VisitorSignupFormTestCase(TestCase):

    def setUp(self):
        self.url = reverse('visitor_signup')
        self.form_input = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.org',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }

    def test_valid_sign_up_form(self):
        form = VisitorSignupForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = VisitorSignupForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('password', form.fields)
        self.assertIn('confirm_password', form.fields)
        self.assertTrue(form.fields['password'].widget, forms.PasswordInput)
        self.assertTrue(form.fields['confirm_password'].widget, forms.PasswordInput)


    def test_password_must_contain_uppercase_character(self):
        self.form_input['password'] = 'password123'
        self.form_input['confirm_password'] = 'password123'
        form = VisitorSignupForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['password'] = 'PASSWORD123'
        self.form_input['confirm_password'] = 'PASSWORD123'
        form = VisitorSignupForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['password'] = 'PasswordABC'
        self.form_input['confirm_password'] = 'PasswordABC'
        form = VisitorSignupForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['confirm_password'] = 'WrongPassword123'
        form = VisitorSignupForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = VisitorSignupForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        # user = User.objects.get(email='johndoe@example.org')
        # self.assertEqual(user.first_name, 'john')
        # self.assertEqual(user.last_name, 'doe')
        # self.assertEqual(user.email, 'johndoe@example.org')
        #is_password_correct = check_password('Password123', user.password)
        #self.assertTrue(is_password_correct)
