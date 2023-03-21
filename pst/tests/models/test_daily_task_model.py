from django.core.exceptions import ValidationError
from django.test import TestCase
from pst.models import DailyTask, DailyTaskStatus, Day, User


class DailyTaskTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']
    def setUp(self):
        self.user = User.objects.get(email='lll@example.org')
        self.day1 = Day.objects.create(number=1)
        self.day2 = Day.objects.create(number=2)
        self.daily_task = DailyTask.objects.create(user=self.user)
        self.daily_task.days.add(self.day1)

    def test_get_day(self):
        self.assertEqual(self.daily_task.get_day().count(), 1)
        self.assertTrue(self.day1 in self.daily_task.get_day())
        self.assertFalse(self.day2 in self.daily_task.get_day())

    def test_get_user(self):
        self.assertEqual(self.daily_task.get_user(), self.user)

    def test_str_method(self):
        self.assertEqual(str(self.daily_task),
                         f"{self.user.email}'s daily tasks")

    def test_invalid_daily_task(self):
        self.daily_task.user = None
        self._assert_daily_task_is_invalid()

    # def test_through_model(self):
    #     daily_task_status = DailyTaskStatus.objects.create(
    #         daily_task=self.daily_task, day=self.day2, status=True)
    #     self.assertEqual(daily_task_status.daily_task, self.daily_task)
    #     self.assertEqual(daily_task_status.day, self.day2)
    #     self.assertTrue(daily_task_status.status)

    def test_daily_task_creation(self):
        daily_task_count = DailyTask.objects.count()
        self.assertEqual(daily_task_count, 1)
        self.assertEqual(self.daily_task.user, self.user)

    def test_daily_task_deletion(self):
        self.daily_task.delete()
        daily_task_count = DailyTask.objects.count()
        daily_task_status_count = DailyTaskStatus.objects.count()
        self.assertEqual(daily_task_count, 0)
        self.assertEqual(daily_task_status_count, 0)

    def _assert_daily_task_is_valid(self):
        try:
            self.daily_task.full_clean()
        except ValidationError:
            self.fail('Test daily task should be valid')

    def _assert_daily_task_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.daily_task.full_clean()

