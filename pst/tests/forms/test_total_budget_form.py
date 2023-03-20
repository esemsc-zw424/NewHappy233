from django.test import TestCase
from pst.models import User, Budget, TotalBudget
from datetime import date, timedelta
from pst.forms import TotalBudgetForm

class TotalBudgetFormTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')


    def test_clean(self):
        form_data = {
            'limit': 5000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=10),
        }
        form = TotalBudgetForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())

        # Test if end_date is set to 30 days later if it is not provided
        form_data = {
            'limit': 5000,
            'start_date': date.today(),
        }
        form = TotalBudgetForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['end_date'], date.today() + timedelta(days=30))

        # Test if existing specific budgets are deleted before adding new one
        existing_budget = TotalBudget.objects.create(limit=5000, start_date='2022-01-01', end_date='2022-12-31', budget_owner=self.user,)
        form_data = {
            'limit': 5000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=10),
        }
        form = TotalBudgetForm(self.user, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(TotalBudget.objects.filter(budget_owner=self.user).count(), 1)