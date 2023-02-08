
from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Categories, User

class CategoriesModelTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.categories = Categories.objects.get(name = 'Food')
        self.spending_owner = User.objects.get(email = "johndoe@example.org")

    def _assert_categories_is_valid(self):
        try:
            self.categories.full_clean()
        except(ValidationError):
            self.fail('Test spending should be valid')

    def _assert_categories_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.categories.full_clean()

    def test_valid_categories(self):
        self._assert_categories_is_valid()

    def test_name_cannot_be_blank(self):
        self.categories.name = ''
        self._assert_categories_is_invalid()

    def test_name_cannot_exceed_100_characters(self):
        self.categories.name = 'x' * 101
        self._assert_categories_is_invalid()

    def test_name_can_be_100_characters(self):
        self.categories.name = 'x' * 100
        self._assert_categories_is_valid()

    def test_spending_owner_cannot_be_blank(self):
        self.categories.owner = None
        self._assert_categories_is_invalid()

    def test_categories_type_cannot_be_blank(self):
        self.categories.categories_type = ''
        self._assert_categories_is_invalid()

    def test_categories_type_can_only_be_one_of_the_choice_Expenditure(self):
        self.categories.categories_type = 'Expenditure'
        self._assert_categories_is_valid()

    def test_categories_type_can_only_be_one_of_the_choice_Income(self):
        self.categories.categories_type = 'Income'
        self._assert_categories_is_valid()

    def test_categories_type_can_only_be_one_of_the_choice_other_text(self):
        self.categories.categories_type = 'xxxx'
        self._assert_categories_is_invalid()

    def test_spending_type_must_not_be_unique(self):
        second_categories = Categories.objects.get(name = 'Drink')
        self.categories.categories_type = second_categories.categories_type
        self._assert_categories_is_valid()

    def test_default_category_is_false(self):
        self.assertEqual(False, self.categories.default_category)

    def test_default_category_can_be_true(self):
        self.categories.default_category == True
        self._assert_categories_is_valid()

    