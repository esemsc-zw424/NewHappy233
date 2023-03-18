from django.test import TestCase, Client
from django.urls import reverse
from pst.models import User
from datetime import date

from pst.forms import TotalBudgetForm
from pst.models import TotalBudget

class SetBudgetViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='test', last_name='user', email='testuser@test.com', password='testpass')
        self.url = reverse('budget_set')
        self.form_input = {
            'name': 'Test Budget',
            'limit': 1000,
            'start_date': date.today(),
            'end_date': date.today(),
        }
        self.client.login(email='testuser@test.com', password='testpass')

    def test_get_set_budget_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'budget_set.html')
        form = response.context['form']
        self.assertTrue(form, TotalBudgetForm)
        self.assertFalse(form.is_bound)

    def test_set_budget_with_valid_data(self):
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, reverse('budget_show'))
        self.assertEqual(TotalBudget.objects.count(), 1)
        budget = TotalBudget.objects.first()
        self.assertEqual(budget.name, 'Test Budget')
        self.assertEqual(budget.limit, 1000)
        self.assertEqual(budget.start_date, date.today())
        self.assertEqual(budget.end_date, date.today())
        self.assertEqual(budget.budget_owner, self.user)