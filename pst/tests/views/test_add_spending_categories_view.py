from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Spending, Categories, User
from pst.forms import CategoriesForm
from django.urls import reverse
from django.shortcuts import render

class AddSpendingCategoriesTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.url = reverse('add_spending_categories')
        self.categories = Categories.objects.get(name = 'Food')
        self.user = User.objects.get(email = "johndoe@example.org")

    def test_add_categories_url(self):
        self.assertEqual(self.url, '/add_spending_categories/')

    def test_access_add_categories_when_log_in_as_user(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_spending_categories.html')
        form = response.context['form']
        self.assertIsInstance(form, CategoriesForm)
        self.assertFalse(form.is_bound)

    # def test_access_add_categories_when_not_log_in(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     redirect_url = reverse('visitor_signup')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)