from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Spending, User

class SpendingModelTestCase(TestCase):

    # this test will test all field in Spending model
    fixtures = ['pst/tests/fixtures/spending.json'], ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.spending_owner = User.objects.get(email = "johndoe@example.org")
        self.spending = Spending.objects.get(descriptions = "This is test spending 1")

    def _assert_spending_is_valid(self):
        try:
            self.spending.full_clean()
        except(ValidationError):
            self.fail('Test spending should be valid')

    def _assert_spending_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.spending.full_clean()

    def test_title_cannot_be_blank(self):
        self.spending.title = ''
        self._assert_spending_is_invalid()

    def test_title_cannot_exceed_30_characters(self):
        self.spending.title = 'x' * 31
        self._assert_spending_is_invalid()

    def test_spending_owner_cannot_be_blank(self):
        self.spending.spending_owner = None
        self._assert_spending_is_invalid()

    def test_spending_amount_cannot_be_blank(self):
        self.spending.amount = ''
        self._assert_spending_is_invalid()

    def test_amount_max_digits(self):
        self.spending.amount = 999999.99
        self._assert_spending_is_valid()
    
    def test_amount_max_digits_cannot_exceed_8_digits(self):
        self.spending.amount = 9999999.99
        self._assert_spending_is_invalid()

    def test_spending_amount_can_be_0(self):
        self.spending.amount = 0
        self._assert_spending_is_valid()
    
    def test_spending_amount_can_be_0(self):
        self.spending.amount = 0
        self._assert_spending_is_valid()
    
    def test_spending_amount_can_be_0(self):
        self.spending.amount = 0
        self._assert_spending_is_valid()

    def test_spending_amount_cannot_be_less_than_0(self):
        self.spending.amount = -1
        self._assert_spending_is_invalid()

    def test_spending_amount_must_not_be_unique(self):
        second_spending = Spending.objects.get(descriptions = "This is test spending 2")
        self.spending.amount = second_spending.amount
        self._assert_spending_is_valid()

    def test_spending_amount_must_only_contain_numbers(self):
        self.spending.amount = 'xxx'
        self._assert_spending_is_invalid()

    def test_amount_must_only_contain_number(self):
        self.spending.amount = 'sss'
        self._assert_spending_is_invalid()

    def test_spending_description_can_be_blank(self):
        self.spending.descriptions = ''
        self._assert_spending_is_valid()

    def test_spending_descriptions_can_be_500_characters_long(self):
        self.spending.descriptions = 'x' * 500
        self._assert_spending_is_valid()

    def test_spending_descriptions_cannot_be_500_characters_long(self):
        self.spending.descriptions = 'x' * 501
        self._assert_spending_is_invalid()

    def test_spending_descriptions_must_not_be_unique(self):
        second_spending = Spending.objects.get(descriptions = "This is test spending 2")
        self.spending.descriptions = second_spending.descriptions
        self._assert_spending_is_valid()

    def test_date_cannot_be_blank(self):
        self.spending.date = None
        self._assert_spending_is_invalid()

    def test_spending_type_cannot_be_blank(self):
        self.spending.spending_type = ''
        self._assert_spending_is_invalid()

    def test_spending_type_can_only_be_one_of_the_choice_Expenditure(self):
        self.spending.spending_type = 'Expenditure'
        self._assert_spending_is_valid()

    def test_spending_type_can_only_be_one_of_the_choice_Income(self):
        self.spending.spending_type = 'Income'
        self._assert_spending_is_valid()

    def test_spending_type_can_only_be_one_of_the_choice_other_text(self):
        self.spending.spending_type = 'xxxx'
        self._assert_spending_is_invalid()

    def test_spending_type_must_not_be_unique(self):
        second_spending = Spending.objects.get(descriptions = "This is test spending 2")
        self.spending.spending_type = second_spending.spending_type
        self._assert_spending_is_valid()
    

    # test of category needs to be implemented later.