from django import forms
from .models import User, Spending
from django.forms import ClearableFileInput

class AddSpendingForm(forms.ModelForm):
    class Meta:
        model = Spending
        fields = ['title', 'amount', 'descriptions', 'date', 'spending_type', 'file',]
        widgets = {'file': ClearableFileInput(attrs={'multiple': True}) }