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
        self.category = Categories.objects.create(
            name='test category',
            categories_type='Expenditure',
            owner=self.user
        )
        self.category_1 = Categories.objects.create(
            name='test category 1',
            categories_type='Income',
            owner=self.user
        )

    def test_add_categories_url(self):
        # Test that the URL for get categories by type is correct
        self.assertEqual(self.url, '/get_categories_by_type/')

    def test_get_categories_by_type_expenditure(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password="Password123")

        # Send a GET request to the view with the 'Expenditure' spending type
        response = self.client.get(self.url, {'spending_type': 'Expenditure'})

        # Check that the response is valid
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Check that the response contains the expected data
        data = response.json()
        self.assertEqual(len(data['categories']), 3) # two in fixtures with type Expenditure

        self.assertEqual(data['categories'][2]['id'], self.category.id) # test category is the 3rd categoreis under the filter that type = expenditure
        self.assertEqual(data['categories'][2]['name'], self.category.name)

    def test_get_categories_by_type_income(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password="Password123")

        # Send a GET request to the view with the 'Income' spending type
        response = self.client.get(self.url, {'spending_type': 'Income'})

        # Check that the response is valid
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Check that the response contains the expected data
        data = response.json()
        self.assertEqual(len(data['categories']), 2) # 1 in fixtures with type Expenditure
        self.assertEqual(data['categories'][1]['id'], self.category_1.id) # test category is the 2nd categoreis under the filter that type = Income
        self.assertEqual(data['categories'][1]['name'], self.category_1.name)





    