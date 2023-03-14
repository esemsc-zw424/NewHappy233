from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Budget, User

class BudgetModelTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        # Create a user to be the owner of the budget
        self.user = self.user = User.objects.get(email='lll@example.org')

        self.budget = Budget.objects.create(
            limit=1000,
            budget_owner=self.user
        )

    def _assert_budget_is_valid(self):
        try:
            self.budget.full_clean()
        except(ValidationError):
            self.fail('Test spending should be valid')

    def _assert_budget_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.budget.full_clean()

    def test_budget_created(self):
        # Check if the budget was created successfully
        self.assertEqual(Budget.objects.count(), 1)
        budget = Budget.objects.first()
        self.assertEqual(budget.limit, 1000)
        self.assertEqual(budget.budget_owner, self.user)

    def test_created_buget_is_valid(self):
        self._assert_budget_is_valid()

    def test_budget_limit_can_exceed_ten_digits(self):
        self.budget.limit = 1000000000000
        self._assert_budget_is_valid()

    def test_budget_deleted_with_user(self):
        # Delete the user and check if the budget is deleted as well
        self.user.delete()
        self.assertEqual(Budget.objects.count(), 0)