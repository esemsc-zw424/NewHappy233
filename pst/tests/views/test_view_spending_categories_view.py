from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Spending, Categories, User
from pst.forms import CategoriesForm
from django.urls import reverse
from django.shortcuts import render

class ViewSpendingCategoriesTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.url = reverse('view_spending_categories')
        self.categories = Categories.objects.get(name = 'Food')
        self.user = User.objects.get(email = "johndoe@example.org")

    def test_view_categories_url(self):
        # Test that the URL for view spending categories is correct
        self.assertEqual(self.url, '/view_spending_categories/')

    def test_view_spending_categories_when_login_as_user(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password="Password123")

        # Test the view for view spending categories is accessable when loggin in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_spending_categories.html')
        self.assertIsInstance(response.context['form'], CategoriesForm)
        self.assertEqual(response.context['categories_expenditure'].count(), 2)
        self.assertEqual(response.context['categories_income'].count(), 1)
        
    def test_view_spending_categories_with_valid_data(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password="Password123")

        # create two new categories
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

        # Test the view for view spending categories is accessable when loggin in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_spending_categories.html')
        self.assertIsInstance(response.context['form'], CategoriesForm)
        self.assertEqual(response.context['categories_expenditure'].count(), 3)
        self.assertEqual(response.context['categories_income'].count(), 2)

