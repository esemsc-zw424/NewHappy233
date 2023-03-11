
from django.contrib import admin
from .models import User, Spending, SpendingFile, Categories, Post, PostImage, Reply, Like
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
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
         'bio', 'gender', 'phone_number', 'address','reward_points')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_staff', 'is_active')}
         ),
    )
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
        'user', 'title', 'content', 'get_num_likes', 'post_date',
    ]
    
    def get_num_likes(self, obj):
        return obj.likes.count()
    get_num_likes.short_description = 'Number of Likes'

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = [
        'post', 'image',
    ]

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'parent_post', 'parent_reply', 'content', 'get_num_likes',
    ]

    def get_num_likes(self, obj):
        return obj.likes.count()
    get_num_likes.short_description = 'Number of Likes'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'content_type', 'object_id'
    ]

