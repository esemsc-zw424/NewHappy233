from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib import messages
from .forms import  CategoriesForm, PostForm, ReplyForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import User ,Categories
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType

from .models import SpendingFile, PostImage, Like
from .forms import *
from django.views import View
from django.utils.decorators import method_decorator
from pst.helpers.auth import login_prohibited
from django.contrib.auth import authenticate, login, logout

import os
from NewHappy.settings import MEDIA_ROOT
from django.http import HttpResponse
import random
import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


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

@login_prohibited
def visitor_introduction(request):
    return render(request, 'visitor_introduction.html')

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        next = request.POST.get('next') or ''
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or 'home'
                return redirect(redirect_url)
       # messages.add_message(request, messages.ERROR,
                            # "The credentials provided are invalid!")
        else:
            next = request.GET.get('next') or ''
    form = LoginForm()
    return render(request, 'log_in.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('visitor_introduction')

#Chatbot is a simple virtual help assistant that can answer user's question base on keywords
def chat_bot(request):
    chat_history = [] # this is use to store all the chat history between user and chatbot
    if request.method == 'POST':
        user_input = request.POST['user_input']
        chat_bot_response = respond(user_input)
        chat_history.append((user_input, chat_bot_response))
        return render(request, 'chat_bot.html', {'chat_history': chat_history})
    return render(request, 'chat_bot.html', {'chat_history': chat_history})

def respond(user_input):
    lemmatizer = WordNetLemmatizer()
    keywords = {
        "pst": ["personal spending tracker", "pst"],
        "budget": ["budget", "spending budget", "financial budget"],
        "expense": ["expense", "spending", "financial expense"],
        "track": ["track", "record", "keep track"],
        "saving": ["saving", "save", "financial saving"],
        "finance": ["finance", "financial management", "money management"],
        "hello": ["hi", "hello", "hey", "greetings", "heya", "hola", "what's up", "sup"],
        "bye": ["bye", "goodbye", "see you later", "adios", "later", "farewell"]
    }

    responses = {
        "pst": ["Our Personal Spending Tracker helps you keep track of your daily expenses and budget."], 
        "budget": ["You can use our Personal Spending Tracker to set budgets for different categories of expenses."], 
        "expense": ["You can log all your expenses on our Personal Spending Tracker, including the date, category, and amount spent. Would you like help tracking an expense?"], 
        "track": ["Our Personal Spending Tracker is designed to help you keep track of your daily expenses, budget, and savings."], 
        "saving": ["Our Personal Spending Tracker can help you track your savings and keep you on track to reach your financial goals."], 
        "finance": ["With the PSC, you can take control of your personal finances and make informed decisions about your spending and saving."],
        "hello": ["Hello! How may I help you?"],
        "bye": ["Goodbye! Have a great day!"],
    }

    for keyword, synonyms in keywords.items():
        if user_input.lower() in [s.lower() for s in synonyms]:
            return random.choice(responses[keyword])

    tokens = word_tokenize(user_input)
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]

    for keyword, synonyms in keywords.items():
        for token in tokens:
            if token in synonyms:
                return random.choice(responses[keyword])
    return "Sorry, I do not understand what you mean."



@login_required
def add_spending(request):
    if request.method == 'POST':
        form = AddSpendingForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            spending = form.save(commit=False)
            spending.spending_owner = request.user
            spending.save()
            for file in request.FILES.getlist('file'):
                SpendingFile.objects.create(
                    spending = spending,
                    file = file
                )
            return redirect('home')
    else:
        form = AddSpendingForm(user=request.user)
    return render(request, 'add_spending.html',  {'form': form})


@login_required
def view_spending(request):
    spending = Spending.objects.all()
    return render(request, 'view_spending.html', {'spending': spending})



@login_required
def add_spending_categories(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit = False)
            category.owner = request.user
            category.save()
            return redirect('home')
    else:
        form = CategoriesForm()
    return render(request, 'add_spending_categories.html',  {'form': form})

@login_required
def view_spending_categories(request):
    if request.method == 'POST':
        delete_spending_categories(request)
    categories_expenditure = Categories.objects.filter(categories_type = Spending_type.EXPENDITURE, owner = request.user)
    categories_income = Categories.objects.filter(categories_type = Spending_type.INCOME, owner = request.user)
    return render(request, 'view_spending_categories.html', {'categories_expenditure': categories_expenditure, 'categories_income': categories_income})

@login_required
def delete_spending_categories(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Categories.objects.get(id=category_id)
        if category.default_category == False:
            category.delete()
        else:
            messages.add_message(request,messages.ERROR,"You can not delete default category!")
        return redirect('view_spending_categories')

@login_required
def update_spending_categories(request, category_id):
    category = Categories.objects.get(id=category_id)
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if category.default_category == False:
            if form.is_valid():
                form = CategoriesForm(request.POST, instance=category)
                form.save()
                return redirect('view_spending_categories')
        else:
            messages.add_message(request,messages.ERROR,"You can not modify default category!")
            return redirect('view_spending_categories')
    else:
        category = Categories.objects.get(id=category_id)
        form = CategoriesForm(instance=category)
    return render(request, 'update_spending_categories.html', {'form': form, 'category': category})

@login_required
def forum(request):
    posts = Post.objects.all().order_by('-post_date')
    for post in posts:
        post.replies = Reply.objects.filter(parent_post=post)
    return render(request, 'forum.html', {'posts': posts})

@login_required
def personal_forum(request):
    posts = Post.objects.filter(user=request.user).order_by('-post_date')
    for post in posts:
        post.replies = Reply.objects.filter(parent_post=post)
    return render(request, 'personal_forum.html', {'posts': posts})

@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit = False)
            post.user = request.user
            post.save()
            for file in request.FILES.getlist('image'):
                PostImage.objects.create(
                    post = post,
                    image = file
                )
            return redirect('forum')
    else:
        form = PostForm()
    return render(request, 'add_post.html',  {'form': form})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {'post': post}
    return render(request, 'post_detail.html', context)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    content_type = ContentType.objects.get_for_model(Post)
    try:
        like = Like.objects.get(
            content_type=content_type,
            object_id=post_id,
            user=user,
        )
        like.delete()
        created = False
    except Like.DoesNotExist:
        like = Like.objects.create(
            content_type=content_type,
            object_id=post_id,
            user=user,
        )
        created = True
    like_count = post.likes.count()
    return redirect('forum')

@login_required
def add_reply_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.parent_post = post
            reply.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = ReplyForm()

    context = {'form': form, 'post': post}
    return render(request, 'add_reply_to_post.html', context)


