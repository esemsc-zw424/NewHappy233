from pst.models import Budget, User
from pst.forms import BudgetForm
from django.test import TestCase, Client
from django.urls import reverse


class SetBudgetTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(first_name='John', last_name='Tester', email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')

    def test_set_budget_with_valid_data(self):
        url = reverse('budget_set')
        data = {
            'limit': 1000
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('budget_show'))
        self.assertEqual(Budget.objects.count(), 1)
        budget = Budget.objects.first()
        self.assertEqual(budget.limit, 1000)
        self.assertEqual(budget.budget_owner, self.user)

    def test_set_budget_with_invalid_data(self):
        url = reverse('budget_set')
        data = {
            'limit': 'invalid'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Budget.objects.count(), 0)

    def test_set_budget_with_empty_data(self):
        url = reverse('budget_set')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'budget_set.html')
        self.assertIsInstance(response.context['form'], BudgetForm)
        self.assertEqual(Budget.objects.count(), 0)