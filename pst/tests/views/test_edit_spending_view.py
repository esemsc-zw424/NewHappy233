from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pst.models import User, Spending, Categories, SpendingFile, Spending_type
from pst.forms import EditSpendingForm
from django.contrib import messages
from datetime import datetime
import os
from django.core.exceptions import ObjectDoesNotExist

class EditSpendingTestCase(TestCase):
    fixtures = [
        'pst/tests/fixtures/users.json'], ['pst/tests/fixtures/spending.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")
        self.category = Categories.objects.create(name='Food', owner=self.user)
        self.spending = Spending.objects.get(spending_owner=self.user)
        self.spending_2 = Spending.objects.create(
            title="Spending 2",
            spending_owner=self.user,
            amount=100,
            date=datetime.today(),
            descriptions='This is test case for deleting file',
            spending_type="Spending_type.EXPENDITURE",
            spending_category=self.category
        )
        self.spending_file = SpendingFile.objects.create(
            spending=self.spending_2,
            file=SimpleUploadedFile('test_file.txt', b'This is a test file'),
        )

        self.url = reverse('edit_spending', kwargs={'spending_id': self.spending.id})
        self.url2= reverse('edit_spending', kwargs={'spending_id': self.spending_2.id})
        self.valid_data = {
            'title': 'Test Case 1',
            'amount': 100,
            'descriptions': 'This is test case 1',
            'date': '2022-12-06',
            'spending_type': 'Expenditure',
            'spending_category': self.category.id,
            'file': SimpleUploadedFile('test_file.txt', b'This is a test file'),
        }
        self.valid_data_2 = {
            'title': 'Test Case 2',
            'amount': 100,
            'descriptions': 'This is test case 1',
            'date': '2022-12-06',
            'spending_type': 'Expenditure',
            'spending_category': self.category.id,
            'delete_file': True
        }

    def test_edit_spending_url(self):
        self.assertEqual(self.url, f'/edit_spending/{self.spending.id}/')
    
    def test_get_edit_spending(self):
        self.client.login(username=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, EditSpendingForm))
      
    def test_edit_spending_with_valid_data_with_file(self):
        self.client.login(username=self.user.email, password="Password123")

        response = self.client.post(self.url, self.valid_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Change made successfully')
        #Check that the spending was actually updated in the database
        spending_count_before = Spending.objects.count() 
        spending_count_after = Spending.objects.count()
        self.assertEqual(spending_count_after, spending_count_before)

        updated_spending = Spending.objects.get(id=self.spending.id)
        self.assertEqual(updated_spending.title, self.valid_data['title'])
        self.assertEqual(updated_spending.amount, self.valid_data['amount'])
        self.assertEqual(updated_spending.descriptions, self.valid_data['descriptions'])
        self.assertEqual(updated_spending.spending_type, self.valid_data['spending_type'])
        self.assertEqual(updated_spending.spending_category.id, self.valid_data['spending_category'])
        self.assertEqual(updated_spending.date, datetime.strptime(self.valid_data['date'], '%Y-%m-%d').date())
        
        self.assertEqual(updated_spending.spending_owner, self.user)
        self.assertEqual(updated_spending.files.count(), 1)
        self.assertEqual(updated_spending.files.first().file.read(), b'This is a test file')
        

    
    def test_edit_spending_with_valid_data_with_delete_file_function(self):
        self.client.login(username=self.user.email, password="Password123")

        response = self.client.post(self.url2, self.valid_data_2, follow=True)
        self.assertEqual(response.status_code, 200)
        
        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Change made successfully')
        #Check that the spending was actually updated in the database
        spending_count_before = Spending.objects.count() 
        spending_count_after = Spending.objects.count()
        self.assertEqual(spending_count_after, spending_count_before)

        updated_spending = Spending.objects.get(id=self.spending_2.id)
        self.assertEqual(updated_spending.title, self.valid_data_2['title'])
        self.assertEqual(updated_spending.amount, self.valid_data_2['amount'])
        self.assertEqual(updated_spending.descriptions, self.valid_data_2['descriptions'])
        self.assertEqual(updated_spending.spending_type, self.valid_data_2['spending_type'])
        self.assertEqual(updated_spending.spending_category.id, self.valid_data_2['spending_category'])
        self.assertEqual(updated_spending.date, datetime.strptime(self.valid_data_2['date'], '%Y-%m-%d').date())
        self.assertEqual(updated_spending.spending_owner, self.user)
        # test if file is successfully delete
        self.assertEqual(updated_spending.files.count(), 0)
    
    def test_spending_not_found(self):
        self.client.login(username=self.user.email, password="Password123")
        spending_id = 99999999999
        self.assertFalse(Spending.objects.filter(id=spending_id).exists())
        temp_url = reverse('edit_spending', kwargs={'spending_id': spending_id})

        redirect_url = reverse('view_spendings')
        response = self.client.get(temp_url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    # def tearDown(self):
    #     # Delete all spending files
    #     for spending_file in SpendingFile.objects.filter(spending__in=[self.spending, self.spending_2]):
    #         spending_file.delete()
        
   
