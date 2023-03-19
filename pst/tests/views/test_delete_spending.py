# from django.test import TestCase, Client
# from django.urls import reverse
#
# from pst.models import Spending, Categories, Spending_type,User
#
#
# class DeleteSpendingTestCase(TestCase):
#     fixtures = [
#         'pst/tests/fixtures/users.json'], ['pst/tests/fixtures/spending.json']
#
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.get(email="johndoe@example.org")
#         self.category = Categories.objects.create(
#             name='testcategory',
#             owner=self.user,
#             categories_type=Spending_type.EXPENDITURE,
#         )
#         self.spending = Spending.objects.create(
#             title='testtitle',
#             spending_owner=self.user,
#             amount=100.00,
#             descriptions='testdescription',
#             date='2022-03-19',
#             spending_type=Spending_type.EXPENDITURE,
#             spending_category=self.category
#         )
#         self.url = reverse('delete_spending', args=[self.spending.id])
#
#     def test_delete_spending(self):
#         self.client.login(username=self.user.email, password="Password123")
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 302)  # check for redirect
#         self.assertFalse(Spending.objects.filter(id=self.spending.id).exists())  # check if spending object still exists
#         messages = list(response.context['messages'])
#         self.assertEqual(len(messages), 1)  # check if message is displayed
#         self.assertEqual(str(messages[0]), 'spending has been deleted')
#
#     def test_delete_spending_unauthenticated(self):
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 302)  # check for redirect
#         self.assertTrue(Spending.objects.filter(id=self.spending.id).exists())  # check if spending object still exists
#         messages = list(response.context['messages'])
#         self.assertEqual(len(messages), 1)  # check if message is displayed
#         self.assertEqual(str(messages[0]), 'Please log in to continue.')
#
#     def tearDown(self):
#         self.spending.delete()
#         self.category.delete()
#         self.user.delete()