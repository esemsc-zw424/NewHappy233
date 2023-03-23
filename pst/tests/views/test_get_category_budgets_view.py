from django.test import TestCase, Client
from pst.models import Categories, Spending_type, User, TotalBudget
from pst.views import get_category_budgets
from datetime import datetime

class TestGetCategoryBudgets(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.category1 = Categories.objects.create(
            name='Groceries', owner=self.user, categories_type=Spending_type.EXPENDITURE)
        self.category2 = Categories.objects.create(
            name='Salary', owner=self.user, categories_type=Spending_type.INCOME)
        self.category3 = Categories.objects.create(
            name='Sport', owner=self.user, categories_type=Spending_type.EXPENDITURE)
        self.category4 = Categories.objects.create(
            name='Entertainment', owner=self.user, categories_type=Spending_type.EXPENDITURE)

    def test_get_category_budgets_with_none_total_budget(self):
        self.client.login(username='lll@example.org', password='Password123')
        total_budget = None
        get_category_budgets(self, total_budget)

    def test_get_category_budgets_with_valid_total_budget(self):
        self.client.login(username='lll@example.org', password='Password123')
        total_budget = TotalBudget.objects.create(limit=1200,
                start_date=datetime.today().replace(day=1),
                end_date=datetime.today().replace(day=30),
                budget_owner=self.user)
        get_category_budgets(self, total_budget)