from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import *
from django.views import View
from django.utils.decorators import method_decorator


# Create your views here.

@login_required
def userFeed(request):
    return render(request, 'userFeed.html')

@login_required
def Add_Spending(request):
    if request.method == 'Post':
        form = AddSpendingForm(request.user, request.POST, request.FILES)
        files = request.FILES.getlist('file')
        if form.is_valid():
            form.save()
        else:
            messages.add_message(request, messages.ERROR, 'Failure, check the information you wrote.')
            return render(request, 'spending_creation.html')
    else:
        form = AddSpendingForm()
    return render(request, 'spending_creation.html', {'form': form})
    