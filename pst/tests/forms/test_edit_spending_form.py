from django import forms
import os
from django.test import TestCase
from pst.forms import EditSpendingForm
from django.core.files.uploadedfile import SimpleUploadedFile
from pst.models import Spending, SpendingFile, User, Categories
from django.urls import reverse
from datetime import date

class EditSpendingFormTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="alicedoe@example.org")
        self.category = Categories.objects.create(name='Food', owner=self.user)
        self.spending = Spending.objects.create(
            spending_owner=self.user,
            title='test spending',
            amount=10,
            descriptions='test description',
            date=date.today(),
            spending_type='test type',
            spending_category=self.category,
        )

        self.form_input = {
            'title': 'Test Case 1',
            'amount': 100,
            'descriptions': 'This is test case 1',
            'date': '2022-12-06',
            'spending_type': 'Expenditure',
            'spending_category': self.category.id,
            'file': SimpleUploadedFile('test_file.txt', b'This is a test file')
        }
        
    

    def test_form_contains_necessary_fields(self):
        form = EditSpendingForm(user=self.user)
        self.assertIn('title', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('descriptions', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('spending_type', form.fields)
        self.assertIn('spending_category', form.fields)
        self.assertIn('file', form.fields)
        self.assertTrue(isinstance(form.fields['spending_category'], forms.ModelChoiceField))
        file = form.fields['file']
        self.assertTrue(isinstance(file.widget, forms.ClearableFileInput))
        self.assertTrue('delete_file', form.fields)
    
    def test_form_with_valid_data(self):
        
        form = EditSpendingForm(user=self.user, data=self.form_input, instance=self.spending)
        self.assertTrue(form.is_valid())
        before_count = User.objects.count()
        spending, created = form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(spending.title, 'Test Case 1')
        self.assertEqual(spending.amount, 100)
        self.assertEqual(spending.descriptions, 'This is test case 1')
        self.assertEqual(spending.date, date(2022, 12, 6))
        self.assertEqual(spending.spending_type, 'Expenditure')
        self.assertEqual(spending.spending_category, self.category)
        file = self.form_input['file']

        SpendingFile.objects.create(spending=spending, file=file)
        self.assertTrue(self.spending.files.all().count(), 1)
        self.assertEqual(self.spending.files.first().file.read(), b'This is a test file')

        # Get the absolute path to the static directory and delete the file
        file_dir = os.path.abspath(os.path.join(__file__, '../../../../static'))
        file_path = os.path.join(file_dir, 'user_files', 'test_file.txt')
        os.remove(file_path)
        self.assertTrue(self.spending.files.all().count(), 0)