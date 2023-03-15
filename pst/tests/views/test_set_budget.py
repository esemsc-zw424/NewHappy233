from pst.models import Budget, User, Categories
from pst.forms import BudgetForm
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone


class SetBudgetTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Tester',
            email='testuser@example.com',
            password='testpass'
        )
        self.category = Categories.objects.get(name = 'Food')
        self.budget = Budget.objects.create(
            name='Test Budget',
            limit=1000,
            start_date=timezone.now(),
            end_date=timezone.now(),
            budget_owner=self.user,
            spending_category=self.category,
        )

    def test_budget_creation(self):
        self.assertEqual(Budget.objects.count(), 1)
        budget = Budget.objects.last()
        self.assertEqual(budget.name, 'Test Budget')
        self.assertEqual(budget.limit, 1000)
        self.assertEqual(budget.budget_owner, self.user)
        self.assertEqual(budget.spending_category, self.category)
        self.assertEqual(str(budget), 'Budget object (1)')

    def test_budget_update(self):
        budget = Budget.objects.first()
        budget.limit = 2000
        budget.save()
        self.assertEqual(Budget.objects.count(), 1)
        budget = Budget.objects.first()
        self.assertEqual(budget.limit, 2000)

    def test_budget_deletion(self):
        budget = Budget.objects.first()
        budget.delete()
        self.assertEqual(Budget.objects.count(), 0)

    def test_budget_string_representation(self):
        budget = Budget.objects.first()
        self.assertEqual(str(budget), 'Budget object (1)')