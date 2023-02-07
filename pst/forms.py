from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm, Form
from pst.models import User, Spending, Categories, Spending_type
from django.forms import ClearableFileInput

class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name', 'owner', 'categories_type']

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
            self.add_error('confirm_password',
                           'Confirmation does not match password.')


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

        Categories.objects.create(
            name = 'Food',
            owner = user,
            categories_type = Spending_type.EXPENDITURE
        )
        Categories.objects.create(
            name = 'Drink',
            owner = user,
            categories_type = Spending_type.EXPENDITURE
        )
        Categories.objects.create(
            name = 'Salary',
            owner = user,
            categories_type = Spending_type.INCOME
        )

        return user


class LoginForm(Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class AddSpendingForm(forms.ModelForm):
    spending_category = forms.ModelChoiceField(queryset=Categories.objects.none(), empty_label=None)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AddSpendingForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['spending_category'].queryset = Categories.objects.filter(
                owner = user, categories_type = self.data.get('spending_type')) # this part filter out categories that belongs to current user

    class Meta:
        model = Spending

        fields = ['title', 'amount', 'descriptions', 'date', 'spending_type', 'spending_category']

    file = forms.FileField(
        label='file',
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
    )
