
from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import User


class UserModelTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(email='johndoe@example.org')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_first_name_cannot_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_last_name_cannot_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(email='lll@example.org')
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()
    
    def test_bio_can_be_blank(self):
        self.user.bio= ''
        self._assert_user_is_valid()
    
    def test_bio_cannot_exceed_500_length(self):
        self.user.bio = 'x' * 501
        self._assert_user_is_invalid()
    
    def test_gnder_can_be_blank(self):
        self.user.gender= ''
        self._assert_user_is_valid()

    def test_gender_must_be_one_of_the_option(self):
        self.user.gender = 'unknown'
        self._assert_user_is_invalid()
    
    def test_phone_number_can_be_blank(self):
        self.user.phone_number= ''
        self._assert_user_is_valid()

    def test_phone_number_cannot_exceed_15_length(self):
        self.user.phone_number = '1' * 15
        self._assert_user_is_invalid()
    
    def test_phone_number_must_be_number(self):
        self.user.phone_number = 'abcdfedad' 
        self._assert_user_is_invalid()

    def test_address_can_be_blank(self):
        self.user.address= ''
        self._assert_user_is_valid()
    
    def test_phone_number_cannot_exceed_100_length(self):
        self.user.phone_number = 'a' * 100
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        self.user.email = ''
        with self.assertRaises(ValidationError):
            self.user.full_clean()
