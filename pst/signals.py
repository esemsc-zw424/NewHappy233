from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Categories, Spending_type

@receiver(user_signed_up)
def create_default_categories(sender, request, user, **kwargs):
    """
    Create default categories for new users who sign up.
    """
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