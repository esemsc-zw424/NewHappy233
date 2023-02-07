from django import forms
from django.test import TestCase
from pst.forms import AddSpendingForm
from pst.models import Spending, SpendingFile, User, Categories
from django.core.files.uploadedfile import TemporaryUploadedFile

class AddSpendingFormTestCase(TestCase):

    fixtures = ['pst/tests/fixtures/users.json'], ['pst/tests/fixtures/categories.json']

    def setUp(self):
        self.spending_owner = User.objects.get(email = "johndoe@example.org")
        #self.categories = Categories.objects.get(name = 'Food')
        self.form_input = {
            'title': 'TestCase 1',
            'amount': 100,
            'descriptions': 'This is test case 1',
            'date': '2022-12-06',
            'spending_type': 'Expenditure',
            #'spending_category': self.categories
        }
    
    def test_form_contains_necessary_fields(self):
        form = AddSpendingForm()
        self.assertIn('title', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('descriptions', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('spending_type', form.fields)
        self.assertIn('file', form.fields)
        self.assertIn('spending_category', form.fields)
        self.assertTrue(isinstance(form.fields['spending_category'], forms.ModelChoiceField))
        file = form.fields['file']
        self.assertTrue(isinstance(file.widget, forms.ClearableFileInput))
    
    def test_valid_form(self):
        form = AddSpendingForm(data = self.form_input)
        self.assertTrue(form.is_valid())
        
           
    
    def test_form_must_be_saved_correctly_with_files(self):
        with TemporaryUploadedFile("test.txt", b"file_content", charset="utf-8", size=len(b"file_content")) as file:
            self.form_input['file'] = file
            form = AddSpendingForm(data=self.form_input)
            
            before_count = Spending.objects.count()
            spending = form.save(commit=False)
            spending.spending_owner = self.spending_owner
            spending.save()
            # spending.spending_category = self.categories
            # spending.save()
            after_count = Spending.objects.count()
            self.assertEqual(after_count, before_count+1)
            self.assertEqual(spending.title, 'TestCase 1')
            self.assertEqual(spending.spending_owner, self.spending_owner)
            self.assertEqual(spending.amount, 100)    
            self.assertEqual(spending.descriptions, 'This is test case 1')

            #test if file is saved correctly
            spending_file = SpendingFile.objects.create(spending=spending, file = form.cleaned_data['file'])
            spending_file.save()
            self.assertEqual(SpendingFile.objects.count(), 1)
            self.assertEqual(SpendingFile.objects.first().spending, spending)
            self.assertEqual(SpendingFile.file.name, 'test.txt')
            self.assertEqual(SpendingFile.file.read(), b"file_content")

            spending_file.file.delete()
            file.close()
   