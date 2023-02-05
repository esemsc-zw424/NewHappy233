from django.contrib import admin
from .models import User, Spending
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'password', 'last_name',
                  'first_name')

@admin.register(User)
class MyUserAdmin(UserAdmin):
    ordering = ('email',)
    form = MyUserChangeForm 
    list_display = [
        'email', 'first_name', 'last_name',
    ]

@admin.register(Spending)
class SpendingAdmin(admin.ModelAdmin):
    
    list_display = [
        'title', 'spending_owner', 'amount', 'descriptions', 'date', 'spending_type', 'file',    
    ]