# from django.test import TestCase
# from pst.models import User
# from datetime import date, timedelta
# from pst.forms import TotalBudgetForm

# class TotalBudgetFormTestCase(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='test_user', email='test_user@example.com', password='testpass')

#     def test_clean(self):
#         form_data = {
#             'limit': 5000,
#             'start_date': date.today(),
#             'end_date': date.today() + timedelta(days=10),
#         }
#         form = TotalBudgetForm(self.user, data=form_data)
#         self.assertTrue(form.is_valid())

#         # Test if end_date is set to 30 days later if it is not provided
#         form_data = {
#             'limit': 5000,
#             'start_date': date.today(),
#         }
#         form = TotalBudgetForm(self.user, data=form_data)
#         self.assertTrue(form.is_valid())
#         self.assertEqual(form.cleaned_data['end_date'], date.today() + timedelta(days=30))

#         # Test if existing specific budgets are deleted before adding new one
#         existing_budget = Budget.objects.create(owner=self.user, name='test', limit=2000)
#         form_data = {
#             'limit': 5000,
#             'start_date': date.today(),
#             'end_date': date.today() + timedelta(days=10),
#         }
#         form = TotalBudgetForm(self.user, data=form_data)
#         self.assertTrue(form.is_valid())
#         self.assertEqual(Budget.objects.filter(owner=self.user).count(), 0)