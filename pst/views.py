from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import render,redirect
from django.contrib import messages
from pst.forms import VisitorSignupForm
from pst.helpers.auth import login_prohibited
from django.shortcuts import render, redirect
from pst.forms import BudgetForm
from .models import Budget

# Create your views here.

@login_required
def user_feed(request):
    return render(request, 'user_feed.html')


def visitor_signup(request):
    if request.method == 'POST':
        form = VisitorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'visitor_signup.html', {'form': form})
    else:
        form = VisitorSignupForm()
        return render(request, 'visitor_signup.html', {'form': form})


@login_required
def home(request):
    return render(request, 'home.html')

def visitor_introduction(request):
    return render(request, 'visitor_introduction.html')

def set_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('budgets')
    else:
        form = BudgetForm()
    return render(request, 'budget_set.html', {'form': form})