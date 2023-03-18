from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Spending, Categories, User
from pst.forms import CategoriesForm
from django.urls import reverse
from django.shortcuts import render

class GetCategoriesByTypeTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.url = reverse('get_categories_by_type')
        self.user = User.objects.get(email="johndoe@example.org")
        self.valid_data = {
            'name': 'Groceries',
            'categories_type': 'Expenditure'
        }
        self.valid_data_1 = {
            'name': 'Travel',
            'categories_type': 'Expenditure'
        }
        self.category = Categories.objects.create(
            name='test category',
            categories_type='Expenditure',
            owner=self.user
        )

    def test_add_categories_url(self):
        self.assertEqual(self.url, '/get_categories_by_type/')

    # def test_get_categories_by_type(self):
    #     # Log in as the test user
    #     self.client.login(username=self.user.email, password='Password123')

    #     # Send a GET request to the view with the 'Expenditure' spending type
    #     url = reverse('get_categories_by_type')
    #     response = self.client.get(url, {'spending_type': 'Expenditure'})

    #     # Check that the response is valid
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    #     # Check that the response contains the expected data
    #     self.assertContains(response, self.category.name)



    