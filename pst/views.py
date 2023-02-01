from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages

# Create your views here.

@login_required
def user_feed(request):
    return render(request, 'user_feed.html')

