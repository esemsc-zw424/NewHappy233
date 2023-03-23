
# from django.test import TestCase
# from django.conf import settings
# import requests_mock

# class TestLoginTaskStatusTestCase(TestCase):
#     def test_get_login_task_status(self):
#         # mock the response from the server
#         with requests_mock.Mocker() as m:
#             url = f"{settings.STATIC_URL}get_login_task_status/"
#             pos = 1
#             expected_response = {"task_statuses": [{"day": "Monday", "completed": True}]}
#             m.get(f"{url}?pos={pos}", json=expected_response)

#             # call the get_login_task_status function and capture the console output
#             captured_output = self._get_console_output(f"get_login_task_status({pos})")

#             # assert that the task point status is fetched correctly
#             self.assertIn("✓", captured_output)
#             self.assertIn("Monday", captured_output)
#             self.assertIn("get!!!", captured_output)

#     def test_update_modal(self):
#         # create a mock task point element
#         task_point = f"<div id='task_point-normal-Monday'></div>"

#         # call the update_modal function and capture the console output
#         captured_output = self._get_console_output("update_modal({task_statuses: [{day: 'Monday', completed: false}]})")

#         # assert that the task point status is updated correctly
#         self.assertIn("x", captured_output)
#         self.assertIn("Monday", captured_output)
#         self.assertIn("miss", captured_output)

    





