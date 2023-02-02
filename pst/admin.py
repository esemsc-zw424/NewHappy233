from django.contrib import admin

from .models import User,Spending


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'last_name',
    ]

@admin.register(Spending)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'spending_owner', 'amount', 'descriptions', 'date', 'spending_type'   
    ]