from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Budget, User, Categories

class BudgetModelTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json'], ['pst/tests/fixtures/categories.json']

    def setUp(self):
        # Create a user to be the owner of the budget
        self.user = self.user = User.objects.get(email='lll@example.org')
        self.category = Categories.objects.get(name='Food')
        self.budget = Budget.objects.create(name='Test Budget', limit=1000, budget_owner=self.user, spending_category=self.category)

    def test_budget_name_label(self):
        budget = Budget.objects.get(id=1)
        field_label = budget._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_budget_limit_label(self):
        budget = Budget.objects.get(id=1)
        field_label = budget._meta.get_field('limit').verbose_name
        self.assertEqual(field_label, 'limit')

    def test_budget_start_date_label(self):
        budget = Budget.objects.get(id=1)
        field_label = budget._meta.get_field('start_date').verbose_name
        self.assertEqual(field_label, 'start date')

    def test_budget_end_date_label(self):
        budget = Budget.objects.get(id=1)
        field_label = budget._meta.get_field('end_date').verbose_name
        self.assertEqual(field_label, 'end date')

    def test_budget_budget_owner_label(self):
        budget = Budget.objects.get(id=1)
        field_label = budget._meta.get_field('budget_owner').verbose_name
        self.assertEqual(field_label, 'budget owner')

    def test_budget_spending_category_label(self):
        budget = Budget.objects.get(id=1)
        field_label = budget._meta.get_field('spending_category').verbose_name
        self.assertEqual(field_label, 'spending category')

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