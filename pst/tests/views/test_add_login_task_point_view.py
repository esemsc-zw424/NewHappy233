from django.conf import settings
import pst.views as views
from pst.models import DailyTask, DailyTaskStatus, Day, TaskType,User
from django.test import TestCase, RequestFactory
from unittest.mock import patch

class AddLoginTaskTestCase(TestCase):

    fixtures = [
        'pst/tests/fixtures/users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email = 'lll@example.org')
        self.login_task = views.create_login_task(self.user)
        self.factory = RequestFactory()

        
    @patch('pst.views.create_login_task')
    @patch('pst.views.create_daily_task_status')
    def test_login_task_created_successfully(self, mock_create_daily_task_status, mock_create_login_task):
        request = self.factory.post('/')
        request.user = self.user
        views.add_login_task_points(request)
        mock_create_login_task.assert_called_once_with(self.user)


    @patch('pst.views.get_number_days_from_register')
    def test_create_task_status_successfully_with_days_less_than_7(self, mock_get_number_days_from_register):
        mock_get_number_days_from_register.return_value = 5
        request = self.factory.post('/')
        request.user = self.user
        request.user.consecutive_login_days = 5
        login_task = views.create_login_task(self.user)
        daily_task_status = views.create_daily_task_status(request, login_task)
        self.assertEqual(daily_task_status.task_points, settings.NORMAL_TASK_POINTS)


    @patch('pst.views.get_number_days_from_register')
    def test_create_task_status_successfully_with_days_more_than_7(self, mock_get_number_days_from_register):
        mock_get_number_days_from_register.return_value = 10
        request = self.factory.post('/')
        request.user = self.user
        request.user.consecutive_login_days = 10
        login_task = views.create_login_task(self.user)
        daily_task_status = views.create_daily_task_status(request, login_task)
        self.assertEqual(daily_task_status.task_points, settings.HIGH_TASK_POINTS)


    def test_json_response_success(self):
        request = self.factory.post('/')
        request.user = self.user
        response = views.add_login_task_points(request)
        self.assertEqual(response.status_code, 200)