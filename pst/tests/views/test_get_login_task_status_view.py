
from django.conf import settings
from django.test import TestCase, RequestFactory

from pst.models import DailyTaskStatus, DailyTask, Day, TaskType, User
from pst.views import GetLoginTaskStatusView


class GetLoginTaskStatusTests(TestCase):
    fixtures = ['pst/tests/fixtures/users.json','pst/tests/fixtures/days.json']


    def setUp(self):
        self.factory = RequestFactory()
        self.day1 = Day.objects.get(number=1)
        self.day2 = Day.objects.get(number=2)
        self.day3 = Day.objects.get(number=3)
        self.user = User.objects.get(email='lll@example.org')
        self.task = DailyTask.objects.create(user=self.user)
        self.daily_task_status_1 = DailyTaskStatus.objects.create(
            day=self.day1,
            task_type=TaskType.LOGIN.name,
            task=self.task,
        )
        self.daily_task_status_2 = DailyTaskStatus.objects.create(
            day=self.day2,
            task_type=TaskType.LOGIN.name,
            task=self.task,
        )
        daily_task_status = DailyTaskStatus.objects.create(
            task=self.task,
            day=self.day3,
            task_points=settings.NORMAL_TASK_POINTS,
            task_type=TaskType.LOGIN.name
        )


    def test_get_login_task_status_no_pos(self):
        request = self.factory.get('/get_login_task_status/')
        request.user = self.user
        view = GetLoginTaskStatusView.as_view()

        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        # Check the response content
        expected_data = {
            "task_statuses": [
                
            ],
        }
        self.assertJSONEqual(response.content, expected_data)

    def test_get_login_task_status_with_pos(self):
        request = self.factory.get('/get_login_task_status/?pos=', {'pos': 2})
        request.user = self.user
        view = GetLoginTaskStatusView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        # Check the response content
        expected_data = {
            "task_statuses": [
                {"day": 1, "completed": True},
                {"day": 2, "completed": True},
            ],
        }
        self.assertJSONEqual(response.content, expected_data)

    def test_get_login_task_status_not_completed(self):
        request = self.factory.get('/get_login_task_status/?pos=', {'pos': 3})
        request.user = self.user
        view = GetLoginTaskStatusView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        # Check the response content
        expected_data = {
            "task_statuses": [
                {"day": 1, "completed": True},
                {"day": 2, "completed": True},
            ],
        }
        self.assertJSONNotEqual(response.content, expected_data)
