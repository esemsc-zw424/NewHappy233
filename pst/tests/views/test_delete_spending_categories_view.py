from django.test import Client, TestCase
from django.contrib import messages
from pst.models import Spending, Categories, User
from pst.forms import CategoriesForm
from django.urls import reverse
from django.shortcuts import render

class DeleteSpendingCategoriesTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.categories = Categories.objects.get(name = 'Food')
        self.user = User.objects.get(email = "johndoe@example.org")
        self.url = reverse('delete_spending_categories', kwargs={'category_id': self.categories.id})


    def test_delete_spending_categories_url(self):
        # Test that the URL for delele spending categories is correct
        self.assertEqual(self.url, f'/delete_spending_categories/{self.categories.id}')

    def test_access_delete_not_default_categories_when_log_in_as_user(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        # Count the number of categories before delete one
        spending_categories_count_before = Categories.objects.count()

        # Test that the view for delete categories is accessible when logged in
        response = self.client.get(self.url, follow=True)
        
        # Test if successfully redirct to view_spending_categories
        self.assertRedirects(response, reverse('view_spending_categories'))
        self.assertEqual(response.status_code, 200)

        # Check that the category was deleted
        with self.assertRaises(Categories.DoesNotExist):
            Categories.objects.get(id=self.categories.id)

        # Test if correct message arise
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Category successfully deleted')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        # Test that a category has been successfully deleted
        spending_categories_count_after = Categories.objects.count()
        self.assertEqual(spending_categories_count_after, spending_categories_count_before - 1)

    def test_access_delete_default_categories_when_log_in_as_user(self):
        # Log in as the test user
        self.client.login(username=self.user.email, password='Password123')

        category_default = Categories.objects.create(
            name='test category',
            categories_type='Expenditure',
            owner=self.user,
            default_category = True
        )

        # Count the number of categories before trying to delete default category
        spending_categories_count_before = Categories.objects.count()

        url = reverse('delete_spending_categories', kwargs={'category_id': category_default.id})

        # Test that the view for delet categories is accessible when logged in
        response = self.client.get(url, follow=True)
        
        # Test if successfully redirct to view_spending_categories
        self.assertRedirects(response, reverse('view_spending_categories'))
        self.assertEqual(response.status_code, 200)

        # Test if correct message arise
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'You can not delete default category!')
        self.assertEqual(messages_list[0].level, messages.ERROR)

        # Test that a default category shouldn't be deleted, therefore the number should stay the same
        spending_categories_count_after = Categories.objects.count()
        self.assertEqual(spending_categories_count_after, spending_categories_count_before)
