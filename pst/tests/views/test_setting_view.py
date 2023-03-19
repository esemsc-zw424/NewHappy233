# from django.contrib.auth.models import User
# from django.test import TestCase
# from django.urls import reverse
# from django.utils import timezone
# from decimal import Decimal
# from ..forms import TotalBudgetForm
# from ..models import Categories, Budget
# from datetime import timedelta


# class ViewSettingsTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser', email='testuser@test.com', password='testpass')

#     def test_view_settings_logged_in(self):
#         self.client.login(username='testuser', password='testpass')
#         url = reverse('view_settings')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'setting_page.html')
#         self.assertIsInstance(response.context['form'], TotalBudgetForm)

#     def test_view_settings_logged_out(self):
#         url = reverse('view_settings')
#         response = self.client.get(url)
#         self.assertRedirects(response, '/accounts/login/?next=' + url)