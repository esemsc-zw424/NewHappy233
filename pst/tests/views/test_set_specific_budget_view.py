from django.test import TestCase, Client
from django.urls import reverse
from pst.models import User
from decimal import Decimal
from pst.models import TotalBudget, Categories, Budget

class SetSpecificBudgetTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.total_budget = TotalBudget.objects.create(limit=5000, start_date='2022-01-01', end_date='2022-12-31', budget_owner=self.user,)
        self.category = Categories.objects.create(name='Groceries', owner=self.user)

    def test_set_specific_budget_success(self):
        # Test setting a specific budget for a category
        data = {'limit': 200, 'spending_category': self.category.id}
        self.client.force_login(self.user)
        response = self.client.post(reverse('set_specific_budget'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('budget_show'))
        self.assertEqual(Budget.objects.filter(spending_category=self.category).count(), 1)
        self.assertEqual(Budget.objects.filter(spending_category=self.category).last().limit, Decimal('200'))

    def test_set_specific_budget_no_total_budget(self):
        # Test trying to set a specific budget when no total budget is set
        TotalBudget.objects.all().delete()
        data = {'limit': 200, 'spending_category': self.category.id}
        self.client.force_login(self.user)
        response = self.client.post(reverse('set_specific_budget'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You need to set a total budget first")

    def test_set_specific_budget_non_existent_category(self):
        # Test trying to set a specific budget for a non-existent category
        data = {'limit': 200, 'spending_category': 999}
        self.client.force_login(self.user)
        response = self.client.post(reverse('set_specific_budget'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")

    def test_set_specific_budget_with_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('set_specific_budget'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("specific_budget_set.html")