from django import forms
from django.test import TestCase
from pst.forms import ReplyForm
from pst.models import Reply

class ReplyFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'content': 'This is the content for reply form'
        }

    def test_valid_categories_form(self):
        form = ReplyForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_categories_form_has_necessary_fields(self):
        form = ReplyForm()
        self.assertIn('content', form.fields)