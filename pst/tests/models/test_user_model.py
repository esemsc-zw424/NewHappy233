
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

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        self.user.email = ''
        with self.assertRaises(ValidationError):
            self.user.full_clean()