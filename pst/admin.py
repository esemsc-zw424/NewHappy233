from django.contrib import admin
from .models import User, Spending, SpendingFile, Categories, Post, PostImage, Reply
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
        'title', 'spending_owner', 'amount', 'descriptions', 'date', 'spending_type', 'spending_category',    
    ]

@admin.register(SpendingFile)
class SpendingFileAdmin(admin.ModelAdmin):
    list_display = [
        'spending', 'file'
    ]

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'owner', 'categories_type', 'default_category',
    ]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'title', 'content', 'likes', 'post_date',
    ]

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = [
        'post', 'image',
    ]

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'parent_post', 'parent_reply', 'content', 'likes',
    ]

