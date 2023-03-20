from django.test import TestCase, RequestFactory

from pst.models import DailyTaskStatus, DailyTask, TaskType, User
from pst.views import get_login_task_status

class GetLoginTaskStatusTests(TestCase):
    fixtures = ['pst/tests/fixtures/users.json']
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(email='lll@example.org')
        self.task = DailyTask.objects.create(user=self.user)
        self.daily_task_status_1 = DailyTaskStatus.objects.create(
            day=1,
            task_type=TaskType.LOGIN.name,
            task=self.task,
        )
        self.daily_task_status_2 = DailyTaskStatus.objects.create(
            day=2,
            task_type=TaskType.LOGIN.name,
            task=self.task,
        )
        daily_task_status = DailyTaskStatus.objects.create(
            task=login_task,
            day=day,
            task_points=normal_task_points,
            task_type=TaskType.LOGIN.name
        )

    def test_get_login_task_status_no_pos(self):
        request = self.factory.get('/get_login_task_status/')
        request.user = self.user
        response = get_login_task_status(request)

        # Assert response status is 200 and content type is JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        # Check the response content
        expected_data = {
            "task_statuses": [
                {"day": 1, "completed": True},
            ],
        }
        self.assertJSONEqual(response.content, expected_data)

    def test_get_login_task_status_with_pos(self):
        request = self.factory.get('/get_login_task_status/?pos=', {'pos': 2})
        request.user = self.user
        response = get_login_task_status(request)

        # Assert response status is 200 and content type is JSON
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
        response = get_login_task_status(request)

        # Assert response status is 200 and content type is JSON
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