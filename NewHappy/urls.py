"""NewHappy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from pst import views
from django.conf import settings 
from django.conf.urls.static import static  


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.visitor_introduction, name = 'visitor_introduction'),
    path('add_spending/', views.add_spending, name = 'add_spending'),
    path('user_feed/', views.user_feed, name = 'user_feed'),
    path('visitor_signup/', views.visitor_signup, name = 'visitor_signup'),
    path('home/', views.home, name = 'home'),
    path('visitor_introduction/', views.visitor_introduction, name='visitor_introduction'),
    path('budget_set/', views.set_budget, name='budget_set'),
    path('budget_show/', views.show_budget, name='budget_show'),
    path('user_guideline/', views.user_guideline, name='user_guideline'),
    path('log_in/', views.log_in, name = 'log_in'),
    path('chat_bot/', views.chat_bot, name = 'chat_bot'),
    path('log_out/', views.log_out, name = 'log_out'),
    path('accounts/', include('allauth.urls')),
    path('view_spendings', views.view_spendings, name = 'view_spendings'),
    path('add_spending_categories/', views.add_spending_categories, name = 'add_spending_categories'),
    path('view_spending_categories', views.view_spending_categories, name = 'view_spending_categories'),
    path('update_spending_categories/<int:category_id>/', views.update_spending_categories, name = 'update_spending_categories'),
    path('edit_spending/<int:spending_id>/', views.edit_spending, name = 'edit_spending'),
    path('delete_spending/<int:spending_id>/', views.delete_spending,name = 'delete_spending'),
    
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    path('forum/', views.forum, name = 'forum'),
    path('add_post/', views.add_post, name = 'add_post'),
    path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('like_post_details/<int:post_id>/', views.like_post_details, name='like_post_details'),
    path('like_reply/<int:reply_id>/<int:post_id>/', views.like_reply, name='like_reply'),
    path('add_reply_to_post/<int:post_id>/', views.add_reply_to_post, name='add_reply_to_post'),
    path('add_reply_to_reply/<int:post_id>/<int:parent_reply_id>/', views.add_reply_to_reply, name='add_reply_to_reply'),
    path('personal_forum/', views.personal_forum, name ='personal_forum'),
    path('view_post_user/<user_id>/<post_id>/', views.view_post_user, name='view_post_user'),



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)