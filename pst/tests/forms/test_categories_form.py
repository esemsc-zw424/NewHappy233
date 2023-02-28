from django import forms
from django.test import TestCase
from pst.forms import CategoriesForm
from pst.models import Categories

class CategoriesFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'name': 'Hiiii',
            'categories_type': 'Income'
        }

    def test_valid_categories_form(self):
        form = CategoriesForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_categories_form_has_necessary_fields(self):
        form = CategoriesForm()
        self.assertIn('name', form.fields)
        self.assertIn('categories_type', form.fields)
        