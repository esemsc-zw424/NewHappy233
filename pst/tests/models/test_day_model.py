from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import Day

class DayModelTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/days.json']
    def setUp(self):
        self.day = Day.objects.get(number=1)

    def test_username_must_be_unique(self):
        self.day2 = Day.objects.get(number=2)
        self.day.number = self.day2.number
        self._assert_day_is_invalid()

    def test_day_string_representation(self):
        day = Day.objects.get(number=1)
        self.assertEqual(str(day), 'Day 1')

    def _assert_day_is_valid(self):
        try:
            self.day.full_clean()
        except ValidationError:
            self.fail('Test day should be valid')

    def _assert_day_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.day.full_clean()