from django.shortcuts import render, redirect
from .forms import  CategoriesForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import User ,Categories


def categories(request):
    if request.method == 'POST':  # create category
        Categories.objects.create(name=request.POST['name'])
        return redirect('categories')
    categories = Categories.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def delete_categories(request, pk):
    # delete category
    Categories.objects.filter(pk=pk).delete()
    return redirect('categories')

def ammend_categories(request, pk):
    # ammend category
    category = Categories.objects.get(pk=pk)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.save()
        return redirect('categories')
    return render(request, 'ammend_category.html', {'category': category})
