from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pst.models import User, Spending, Categories, SpendingFile
from pst.forms import AddSpendingForm
import os

class AddSpendingTestCase(TestCase):
    fixtures = ['pst/tests/fixtures/users.json'], ['pst/tests/fixtures/spending.json']
    
    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")
        self.url = reverse('add_spending')
        self.categories = Categories.objects.create(name='Groceries',
        owner=self.user,
        categories_type="EXPENDITURE",
        default_category=False,)
        self.valid_data = {
            'title': 'Test Case 1',
            'amount': 100,
            'descriptions': 'This is test case 1',
            'date': '2022-12-06',
            'spending_type': 'Expenditure',
            'spending_category': self.categories.id,
    }

    #add_spending is made as a modal in view_spendings.html
    def test_add_spending_url(self):
        self.assertEqual(self.url,'/add_spending/')

    def test_get_add_spending(self):
        self.client.login(username=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, AddSpendingForm))
        self.assertFalse(form.is_bound)
    
    def test_add_spending_with_valid_data(self):
        # Ensure that a new spending object is created with valid data
        self.client.login(username=self.user.email, password="Password123")
       
        spending_count_before = Spending.objects.count()
        
        response = self.client.post(self.url, self.valid_data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Spending added successfully')
        spending_count_after = Spending.objects.count()
        
        self.assertEqual(spending_count_after, spending_count_before + 1)
        new_spending = Spending.objects.last()
        self.assertEqual(new_spending.title, 'Test Case 1')
        self.assertEqual(new_spending.descriptions, 'This is test case 1')
        self.assertEqual(new_spending.amount, 100)
        self.assertEqual(new_spending.date.strftime('%Y-%m-%d'), '2022-12-06')
        self.assertEqual(new_spending.spending_owner, self.user)