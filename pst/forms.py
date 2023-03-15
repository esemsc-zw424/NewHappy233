from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm, Form
from pst.models import User, Spending, Categories, Spending_type, Budget, Post, Reply
from django.forms import ClearableFileInput
from django.contrib import messages
from datetime import date


class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name', 'categories_type']


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
        fields = ['email', 'first_name', 'last_name', 'bio', 'gender']
        widgets = {'bio': forms.Textarea()}

    def save(self, commit=False):
        """Create a new user"""

        super().save(commit)
        data = self.cleaned_data
        user = User.objects.create_user(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            password=data.get('password'),
            bio=data.get('bio'),
            gender=data.get('gender'),
        )

        categories = [
            {'name': 'Food', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Drink', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Transport', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Sport', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Entertainment', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Clothes', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Medical', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Housing', 'type': Spending_type.EXPENDITURE,
                'default_category': True},
            {'name': 'Salary', 'type': Spending_type.INCOME, 'default_category': True},
            {'name': 'Investment', 'type': Spending_type.INCOME,
                'default_category': True},
            {'name': 'Part-Time', 'type': Spending_type.INCOME,
                'default_category': True},
            {'name': 'Other', 'type': Spending_type.INCOME, 'default_category': True},
        ]

        for category in categories:
            Categories.objects.create(
                name=category['name'],
                owner=user,
                categories_type=category['type'],
                default_category=category['default_category']
            )

        return user


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio',
                  'gender', 'phone_number', 'address']
        widgets = {'bio': forms.Textarea()}


class LoginForm(Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class AddSpendingForm(forms.ModelForm):

    spending_category = forms.ModelChoiceField(
        queryset=Categories.objects.none(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AddSpendingForm, self).__init__(*args, **kwargs)
        if user:
            spending_type = self.data.get('spending_type', '')
            self.fields['spending_category'].queryset = Categories.objects.filter(
                owner=user)  # this part filter out categories that belongs to current user
        
    class Meta:
        model = Spending
        fields = ['title', 'amount', 'descriptions',
                  'date', 'spending_type', 'spending_category']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'value': date.today().strftime('%Y-%m-%d')}),
        }

    file = forms.FileField(
        label='file',
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
    )


class EditSpendingForm(forms.ModelForm):

    class Meta:
        model = Spending
        fields = ['title', 'amount', 'descriptions',
                  'date', 'spending_type', 'spending_category']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    file = forms.FileField(
        label='file',
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EditSpendingForm, self).__init__(*args, **kwargs)
        if user:
            spending_type = self.data.get('spending_type', '')
            self.fields['spending_category'].queryset = Categories.objects.filter(
                owner=user)  # this part filter out categories that belongs to current user
        self.fields['date'].initial = date.today()

    def save(self):
        if self.is_valid():

            spending = Spending.objects.update_or_create(
                id=self.instance.id,
                defaults={
                    'spending_owner': self.user,
                    'title': self.cleaned_data.get('title'),
                    'amount': self.cleaned_data.get('amount'),
                    'descriptions': self.cleaned_data.get('descriptions'),
                    'date': self.cleaned_data.get('date'),
                    'spending_type': self.cleaned_data.get('spending_type'),
                    'spending_category': self.cleaned_data.get('spending_category'),
                }
            )
            return spending

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'limit']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

    image = forms.ImageField(
        label='image',
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
    )


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content', 'parent_reply']
        widgets = {'parent_reply': forms.HiddenInput()}
