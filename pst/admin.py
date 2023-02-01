from django.contrib import admin
from .models import User, Spending, Categories
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'email', 'username'
    ]

@admin.register(Spending)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'spending_owner', 'amount', 'descriptions', 'date', 'spending_type'   
    ]

@admin.register(Categories)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user'
    ]