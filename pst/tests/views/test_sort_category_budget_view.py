from django.test import Client
from django.test import TestCase
from pst.models import Categories, Spending_type, User
from pst.views import sort_category_budget

class TestSortCategoryBudgets(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(email='lll@example.org')
        self.category_budgets = []
        self.categories = Categories.objects.create(
            name='Groceries', owner=self.user, categories_type=Spending_type.EXPENDITURE)

        self.cg = Categories.objects.filter(owner=self.user, categories_type=Spending_type.EXPENDITURE)
        # Iterate through your data and append new dictionary items to the list
        for category in self.cg:
            self.category_budgets.append({
                'name': 'string',
                'budget': '100',
                'spending': '100',
                'percentage': '75',
            })

    def test_sort_category_budget_with_negative_budget(self):
        selected_sort = '-budget'
        sort_category_budget(self, selected_sort, self.category_budgets)

    def test_sort_category_budget_with_positive_budget(self):
        selected_sort = 'budget'
        sort_category_budget(self, selected_sort, self.category_budgets)

    def test_sort_category_budget_with_negative_spending(self):
        selected_sort = '-spending'
        sort_category_budget(self, selected_sort, self.category_budgets)

    def test_sort_category_budget_with_positive_spending(self):
        selected_sort = 'spending'
        sort_category_budget(self, selected_sort, self.category_budgets)

    def test_sort_category_budget_with_empty_string(self):
        selected_sort = ''
        sort_category_budget(self, selected_sort, self.category_budgets)