# from django.contrib.staticfiles.testing import LiveServerTestCase
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
#
# class DailyLoginTaskTestCase(LiveServerTestCase):
#
#     def setUp(self):
#         self.selenium = webdriver.Chrome()
#         self.selenium.get("http://127.0.0.1:8000/home/")
#
#         # Trigger the show_login_task_modal function by clicking a button or another element
#         trigger_element = self.selenium.find_element_by_id("login_task")
#         trigger_element.click()
#
#         # Wait for the modal to be shown
#         WebDriverWait(self.selenium, 10).until(
#             EC.visibility_of_element_located((By.ID, "daily_login_task"))
#         )
#
#     def tearDown(self):
#         self.selenium.quit()
#
#     def test_show_login_task_modal(self):
#
#         # Assert the modal is visible
#         modal = self.selenium.find_element_by_id("daily_login_task")
#         self.assertTrue(modal.is_displayed())






