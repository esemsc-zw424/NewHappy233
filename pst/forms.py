from django import forms
from django.core.validators import RegexValidator
from .models import User, Categories
from django.core import validators

class CategoriesForm(forms.ModelForm):
     class Meta: model =  Categories = ['name','user']