from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from .models import Categories, Spending_type
from django.contrib.auth.models import Group


@receiver(user_logged_in)
def create_default_categories(sender, request, user, **kwargs):
    if user.categories_created:
        return
    # Create the categories and set the flag
    user.categories_created = True
    user.save()
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
        Categories.objects.create(user=user, **category)