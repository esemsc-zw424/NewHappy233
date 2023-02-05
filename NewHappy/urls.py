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
    path('spending_creation/', views.Add_Spending, name = 'spendingCreation'),
    path('user_feed/', views.user_feed, name = 'user_feed'),
    path('visitor_signup/', views.visitor_signup, name = 'visitor_signup'),
    path('home/', views.home, name = 'home'),
    path('visitor_introduction/', views.visitor_introduction, name = 'visitor_introduction'),
    path('chat_bot/', views.chat_bot, name = 'chat_bot'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)