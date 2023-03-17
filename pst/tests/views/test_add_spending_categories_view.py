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
        self.valid_data = {
            'name': 'Groceries',
            'categories_type': 'Expenditure'
        }

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

    def test_add_spending_categories_view_Expenditure(self):
        self.client.login(username=self.user.email, password="Password123")

        spending_categories_count_before = Categories.objects.count()

        response = self.client.post(self.url, self.valid_data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Category successfully added')
        spending_categories_count_after = Categories.objects.count()
        self.assertEqual(spending_categories_count_after, spending_categories_count_before + 1)

        category = Categories.objects.last()
        self.assertEqual(category.owner, self.user)
        self.assertEqual(category.categories_type, 'Expenditure')

    def test_add_spending_categories_view_Income(self):
        self.client.login(username=self.user.email, password="Password123")

        self.valid_data['categories_type'] = 'Income'

        spending_categories_count_before = Categories.objects.count()

        response = self.client.post(self.url, self.valid_data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Category successfully added')
        spending_categories_count_after = Categories.objects.count()
        self.assertEqual(spending_categories_count_after, spending_categories_count_before + 1)

        category = Categories.objects.last()
        self.assertEqual(category.owner, self.user)
        self.assertEqual(category.categories_type, 'Income')
            
    # def test_access_add_categories_when_not_log_in(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     redirect_url = reverse('visitor_signup')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)