from django import forms
from django.test import TestCase
from pst.forms import PostForm
from pst.models import Post

class PostFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'title': 'Hiiii',
            'content': 'This is the content for post form'
        }

    def test_valid_categories_form(self):
        form = PostForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_categories_form_has_necessary_fields(self):
        form = PostForm()
        self.assertIn('title', form.fields)
        self.assertIn('content', form.fields)