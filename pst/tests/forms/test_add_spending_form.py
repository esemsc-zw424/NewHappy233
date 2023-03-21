import os
from django import forms
from django.test import TestCase
from pst.forms import AddSpendingForm
from datetime import date
from pst.models import Spending, SpendingFile, User, Categories
from django.core.files.uploadedfile import SimpleUploadedFile


class AddSpendingFormTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="alicedoe@example.org")
        self.category = Categories.objects.create(name='Food', owner=self.user)
        self.form_input = {
            'title': 'Test Case 1',
            'amount': 100,
            'descriptions': 'This is test case 1',
            'date': '2022-12-06',
            'spending_type': 'Expenditure',
            'spending_category': self.category.id,
        }

    def test_form_contains_necessary_fields(self):
        form = AddSpendingForm()
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

    def test_form_with_valid_data(self):
        
        form = AddSpendingForm(data=self.form_input, user=self.user)
        self.assertTrue(form.is_valid())
        spending = form.save(commit=False)
        spending.owner = self.user
        spending.save()
        self.assertEqual(spending.title, 'Test Case 1')
        self.assertEqual(spending.amount, 100)
        self.assertEqual(spending.descriptions, 'This is test case 1')
        self.assertEqual(spending.date, date(2022, 12, 6))
        self.assertEqual(spending.spending_type, 'Expenditure')
        self.assertEqual(spending.spending_category, self.category)
