from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import User,  UserProfile


class UserProileTestCase(TestCase):

    fixtures = ['pst/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')

    def test_user_profile_model(self):
        # create user profile
        user_profile = UserProfile.objects.create(
            user=self.user,
            bio='test bio',
            gender='M',
            location='test location',
            birth_date='2000-01-01',
            phone_number='1234567890'
        )

        self.assertTrue(isinstance(user_profile, UserProfile))

        self.assertEqual(str(user_profile), str(self.user))

    def test_gender_choices(self):
        # check if gender choices are correct
        self.assertEqual(UserProfile.GENDER_CHOICES, [
                        ('M', 'Male'), ('F', 'Female'), ('PNTS', 'Perfer not to say')])

    def test_bio_max_length(self):
        # check if bio field has a max length of 500
        user_profile = UserProfile.objects.create(
            user=self.user, bio='x' * 501)
        self.assertEqual(user_profile.bio, 'x' * 500)

    def test_phone_number_max_length(self):
        # check if phone_number field has a max length of 15
        user_profile = UserProfile.objects.create(
            user=self.user, phone_number='x' * 16)
        self.assertEqual(user_profile.phone_number, 'x' * 15)
