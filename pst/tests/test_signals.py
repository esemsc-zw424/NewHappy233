from django.contrib.auth import get_user_model
from django.test import TestCase
from allauth.account.signals import user_signed_up
from pst.models import Categories, Spending_type, User
from pst.signals import create_default_categories

class SignalTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/reply.json']

    def setUp(self):
        self.user = User.objects.get(email = "johndoe@example.org")

    def test_create_default_categories(self):
        # Register a new user
        user = User.objects.create_user(first_name='test', last_name='user', email='testuser@test.com', password='testpass')

        # Trigger the user_signed_up signal to create default categories for the new user
        create_default_categories(sender=None, request=None, user=user)

        # Check that the default categories have been created for the new user
        categories = Categories.objects.filter(owner=user)
        self.assertEqual(categories.count(), 12)
        self.assertTrue(categories.filter(name='Food').exists())
        self.assertTrue(categories.filter(name='Drink').exists())
        self.assertTrue(categories.filter(name='Transport').exists())
        self.assertTrue(categories.filter(name='Sport').exists())
        self.assertTrue(categories.filter(name='Entertainment').exists())
        self.assertTrue(categories.filter(name='Other').exists())
        self.assertTrue(categories.filter(name='Clothes').exists())
        self.assertTrue(categories.filter(name='Medical').exists())
        self.assertTrue(categories.filter(name='Housing').exists())
        self.assertTrue(categories.filter(name='Salary').exists())
        self.assertTrue(categories.filter(name='Investment').exists())
        self.assertTrue(categories.filter(name='Part-Time').exists())

