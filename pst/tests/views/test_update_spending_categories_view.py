from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Spending, Categories, User
from pst.forms import CategoriesForm
from django.urls import reverse
from django.shortcuts import render

class UpdateSpendingCategoriesTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.category = Categories.objects.get(name='Food')
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('update_spending_categories', kwargs={'category_id': self.category.id})
        self.valid_data = {
            'name': 'Updated Category Name',
            'categories_type': 'Expenditure'
        }

    def test_update_spending_categories_url(self):
        # Test that the URL for update spending categories is correct
        self.assertEqual(self.url, f'/update_spending_categories/{self.category.id}/')

    def test_access_update_not_default_categories_expenditure_when_log_in_as_user(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the view for update categories is accessible when logged in
        response = self.client.get(self.url, follow = True)

        # Test that the response is valid
        self.assertEqual(response.status_code, 200)

        # Test that the form is bound with the category data
        form = response.context['form']
        self.assertIsInstance(form, CategoriesForm)
        self.assertFalse(form.is_bound)

        # Test that the form is not valid when the name is empty
        data = {
            'name': '',
            'categories_type': 'Expenditure'
        }
        form = CategoriesForm(data, instance=self.category)
        self.assertFalse(form.is_valid())

        # Test that the form is valid when the data is correct
        data = {
            'name': 'Updated Category Name',
            'categories_type': 'Expenditure'
        }
        form = CategoriesForm(data, instance=self.category)
        self.assertTrue(form.is_valid())

        # Test that the category is updated correctly
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        messages_list = list(response.context.get('messages'))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Change made successfully')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        category = Categories.objects.get(id=self.category.id)
        self.assertEqual(category.name, data['name'])
        self.assertEqual(category.categories_type, data['categories_type'])

    def test_access_update_not_default_categories_income_when_log_in_as_user(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Test that the view for update categories is accessible when logged in
        response = self.client.get(self.url, follow = True)

        # Test that the response is valid
        self.assertEqual(response.status_code, 200)

        # Test that the form is bound with the category data
        form = response.context['form']
        self.assertIsInstance(form, CategoriesForm)
        self.assertFalse(form.is_bound)

        # Test that the form is not valid when the name is empty
        data = {
            'name': '',
            'categories_type': 'Income'
        }
        form = CategoriesForm(data, instance=self.category)
        self.assertFalse(form.is_valid())

        # Test that the form is valid when the data is correct
        data = {
            'name': 'Updated Category Name',
            'categories_type': 'Income'
        }
        form = CategoriesForm(data, instance=self.category)
        self.assertTrue(form.is_valid())

        # Test that the category is updated correctly
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        messages_list = list(response.context.get('messages'))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Change made successfully')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        category = Categories.objects.get(id=self.category.id)
        self.assertEqual(category.name, data['name'])
        self.assertEqual(category.categories_type, data['categories_type'])

    def test_access_update_default_categories_expenditure_when_log_in_as_user(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Create a new default category
        category_default = Categories.objects.create(
            name='test category',
            categories_type='Expenditure',
            owner=self.user,
            default_category=True
        )

        url = reverse('update_spending_categories', kwargs={'category_id': category_default.id})

        # Test that the view for updating categories is accessible when logged in
        response = self.client.get(url, follow=True)

        # Test that the view returns a success status code
        self.assertEqual(response.status_code, 200)

        # Check that the form is the correct form and is bound to the category data
        form = response.context['form']
        self.assertIsInstance(form, CategoriesForm)
        self.assertFalse(form.is_bound)

        # Modify the data for the category
        modified_data = {
            'name': 'test category modified',
            'categories_type': 'Expenditure'
        }

        # Send a POST request to the view to update the category
        response = self.client.post(url, modified_data, follow=True)

        # Test that the view returns a success status code and a success message
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context.get('messages'))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'You can not modify default category!')
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Test that the user is redirected to the view spending categories page
        self.assertRedirects(response, reverse('view_spending_categories'))

    def test_access_update_default_categories_income_when_log_in_as_user(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Create a new default category
        category_default = Categories.objects.create(
            name='test category',
            categories_type='Expenditure',
            owner=self.user,
            default_category=True
        )

        url = reverse('update_spending_categories', kwargs={'category_id': category_default.id})

        # Test that the view for updating categories is accessible when logged in
        response = self.client.get(url, follow=True)

        # Test that the view returns a success status code
        self.assertEqual(response.status_code, 200)

        # Check that the form is the correct form and is bound to the category data
        form = response.context['form']
        self.assertIsInstance(form, CategoriesForm)
        self.assertFalse(form.is_bound)

        # Modify the data for the category
        modified_data = {
            'name': 'test category modified',
            'categories_type': 'Income'
        }

        # Send a POST request to the view to update the category
        response = self.client.post(url, modified_data, follow=True)

        # Test that the view returns a success status code and a success message
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context.get('messages'))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'You can not modify default category!')
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Test that the user is redirected to the view spending categories page
        self.assertRedirects(response, reverse('view_spending_categories'))