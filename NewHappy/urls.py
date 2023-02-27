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
from django.urls import path
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
    path('log_in/', views.log_in, name = 'log_in'),
    path('chat_bot/', views.chat_bot, name = 'chat_bot'),
    path('log_out/', views.log_out, name = 'log_out'),
    path('view_spending', views.view_spending, name = 'view_spending'),
    path('add_spending_categories/', views.add_spending_categories, name = 'add_spending_categories'),
    path('view_spending_categories', views.view_spending_categories, name = 'view_spending_categories'),
    path('update_spending_categories/<int:category_id>/', views.update_spending_categories, name = 'update_spending_categories'),

    path('forum/', views.forum, name = 'forum'),
    path('add_post/', views.add_post, name = 'add_post'),
    path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('like_post/', views.like_post, name='like_post'),
    path('add_reply_to_post/<int:post_id>/', views.add_reply_to_post, name='add_reply_to_post'),
    path('personal_forum/', views.personal_forum, name ='personal_forum'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)