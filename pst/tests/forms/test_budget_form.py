from django.test import TestCase
from pst.models import User
from datetime import datetime, timedelta
from decimal import Decimal
from pst.forms import BudgetForm
from pst.models import Categories, Spending_type, Budget, TotalBudget
from pst.models import User as PSTUser

class BudgetFormTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')
        self.category = Categories.objects.create(
            owner=self.user,
            name='Test Category',
            categories_type=Spending_type.EXPENDITURE,
            default_category=False
        )
        self.total_budget = TotalBudget.objects.create(
            budget_owner=self.user,
            limit=Decimal('1000.00'),
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=30)
        )

    def test_valid_budget_form(self):
        data = {
            'limit': '500.00',
            'spending_category': self.category.id,
        }
        form = BudgetForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_budget_form(self):
        data = {
            'limit': '2000.00',
            'spending_category': self.category.id,
        }
        form = BudgetForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        # self.assertEqual(form.errors['limit'], ["I'm sorry, but you have gone over your total budget limit. Your remaining budget allocation is: (1000.00 + Your last budget for this category, which is: 0). Which means your set here can't exceed: 1000.00"])