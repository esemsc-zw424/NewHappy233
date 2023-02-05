
from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm, Form
from pst.models import User, Budget




class PasswordValidationForm(forms.ModelForm):
    """Auxiliary form for password validation"""

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
                message='Password must contain an uppercase character, a lowercase character and a number.'
            )
        ]
    )

    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
                message='Password must contain an uppercase character, a lowercase character and a number.'
            )
        ]
    )

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            self.add_error('confirm_password', 'Confirmation does not match password.')

    
class VisitorSignupForm(PasswordValidationForm):
    """Form enabling a visitor to sign up"""

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def save(self, commit=False):
        """Create a new user"""

        super().save(commit)
        data = self.cleaned_data
        user = User.objects.create_user(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            password=data.get('password'),
        )
        return user


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'limit']