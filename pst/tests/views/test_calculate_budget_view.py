from django.test import TestCase
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal
from pst.models import User
from pst.models import Spending, TotalBudget, Spending_type, Categories
from pst.views import calculate_budget

class CalculateBudgetTest(TestCase):
    fixtures = ['pst/tests/fixtures/users.json'], ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')
        self.budget = TotalBudget.objects.create(budget_owner=self.user, limit=1000)
        self.categories = Categories.objects.get(name='Food')
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.last_week = self.today - timedelta(days=7)
        self.spending1 = Spending.objects.create(title='Spending 1', amount=Decimal('100'), date=self.yesterday, spending_type=Spending_type.EXPENDITURE, spending_owner=self.user, spending_category=self.categories)
        self.spending2 = Spending.objects.create(title='Spending 2', amount=Decimal('200'), date=self.last_week, spending_type=Spending_type.EXPENDITURE, spending_owner=self.user, spending_category=self.categories)
        self.spending3 = Spending.objects.create(title='Spending 3', amount=Decimal('300'), date=self.yesterday, spending_type=Spending_type.INCOME, spending_owner=self.user, spending_category=self.categories)

    def test_calculate_budget_with_budget(self):
        self.budget.start_date = self.last_week
        self.budget.end_date = self.today
        self.budget.save()
        spending_percentage = calculate_budget(self)
        self.assertEqual(spending_percentage, 30)

    def test_calculate_budget_without_budget(self):
        self.budget.delete()
        spending_percentage = calculate_budget(self)
        self.assertEqual(spending_percentage, 0)

    def test_calculate_budget_without_spending(self):
        self.budget.start_date = self.last_week
        self.budget.end_date = self.today
        self.budget.save()
        self.spending1.clean()
        self.spending2.clean()
        spending_percentage = calculate_budget(self)
        self.assertEqual(spending_percentage, 30)

    def test_calculate_budget_with_income_spending(self):
        self.budget.start_date = self.last_week
        self.budget.end_date = self.today
        self.budget.save()
        spending_percentage = calculate_budget(self)
        self.assertEqual(spending_percentage, 30)
