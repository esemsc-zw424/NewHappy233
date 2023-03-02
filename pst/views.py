from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from django.contrib.auth.decorators import login_required
from django.contrib import auth

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib import messages
from pst.forms import CategoriesForm, AddSpendingForm, LoginForm, EditProfileForm, PostForm, ReplyForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import User, Categories
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
import datetime



from .models import User, Categories, SpendingFile, Reward, Budget, RewardPoint, SpendingFile, PostImage, Like

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
from django.db.models import Sum


# Create your views here.


@login_required
def user_feed(request):
    return render(request, 'user_feed.html')


def visitor_signup(request):
    if request.method == 'POST':
        form = VisitorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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

# Chatbot is a simple virtual help assistant that can answer user's question base on keywords


def chat_bot(request):
    chat_history = []  # this is use to store all the chat history between user and chatbot
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


# @login_required
# def add_spending(request):
#     if request.method == 'POST':
#         form = AddSpendingForm(request.POST, request.FILES)
#         if form.is_valid():
#             spending = form.save(commit=False)
#             spending.spending_owner = request.user
#             for file in request.FILES.getlist('file'):
#                 spending.file = file
#             spending.save()
#             return redirect('home')
#     else:
#         form = AddSpendingForm()
#     return render(request, 'add_spending.html',  {'form': form})


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
                    spending=spending,
                    file=file
                )
            return redirect('home')
    else:
        form = AddSpendingForm(user=request.user)
    return render(request, 'add_spending.html',  {'form': form})


@login_required
def view_spending(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        spending = Spending.objects.filter(date__range=[start_date, end_date]).order_by('date')
    else:
        spending = Spending.objects.all().order_by('date')

    paginator = Paginator(spending, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'spending': spending, 'page_obj': page_obj}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'spending_table.html', context)
    else:
        return render(request, 'view_spending.html', context)


@login_required
def add_spending_categories(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
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
    categories_expenditure = Categories.objects.filter(
        categories_type=Spending_type.EXPENDITURE, owner=request.user)
    categories_income = Categories.objects.filter(
        categories_type=Spending_type.INCOME, owner=request.user)
    return render(request, 'view_spending_categories.html', {'categories_expenditure': categories_expenditure, 'categories_income': categories_income})


@login_required
def delete_spending_categories(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Categories.objects.get(id=category_id)
        if category.default_category == False:
            category.delete()
        else:
            messages.add_message(request, messages.ERROR,
                                 "You can not delete default category!")
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
            messages.add_message(request, messages.ERROR,
                                 "You can not modify default category!")
            return redirect('view_spending_categories')
    else:
        category = Categories.objects.get(id=category_id)
        form = CategoriesForm(instance=category)
    return render(request, 'update_spending_categories.html', {'form': form, 'category': category})

@login_required
def user_profile(request):
    user = request.user
    return render(request, 'user_profile.html', {'user': user})


@login_required
def edit_profile(request):
    try:
        user = request.user
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "User does not exist.")
        return redirect('show_user')

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            user.save()
            return redirect('user_profile')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def user_guideline(request):
    return render(request, 'user_guideline.html')

@login_required
def set_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.budget_owner = request.user
            print(budget.budget_owner_id)
            budget.save()
            return redirect('budget_show')
    else:
        form = BudgetForm()
    return render(request, 'budget_set.html', {'form': form})

@login_required
def show_budget(request):
    total = Spending.objects.aggregate(nums=Sum('amount')).get('nums')
    budget = Budget.objects.filter(budget_owner=request.user).last()
    if budget == None:
        spending_percentage = 0
    elif total == None:
        messages.add_message(request, messages.INFO, 'you have not spent yet')
        spending_percentage = 0
    else:
        spending_percentage = int((total / budget.limit) * 100)
        if spending_percentage >= 100:
            messages.add_message(request, messages.INFO, 'you have exceeded the limit')
    return render(request, 'budget_show.html', {'budget': budget, 'spending_percentage': spending_percentage})

# @login_required
# def cal_spending():
#      spending_total = Spending.objects.aggregate(nums=Sum('amount')).get('nums')
#      return spending_total

@login_required
def index(request):
    if Reward.objects.count() == 0:
        Reward.objects.create(name='Discount coupon', points_required=10)
        Reward.objects.create(name='Free T-shirt', points_required=20)
        Reward.objects.create(name='Gift card', points_required=50)

    rewards = Reward.objects.all()
    rewards_points = RewardPoint.objects.filter(user=request.user).filter()
    context = {
        'rewards': rewards,
        'reward_points': rewards_points,
    }
    return render(request, 'index.html', context)

@login_required
def redeem(request, reward_id):
    reward = Reward.objects.get(id=reward_id)
    reward_points = RewardPoint.objects.filter(user=request.user).first()

    error_message = "You don't have enough reward points to redeem this reward."
    context = {
        'error_message': error_message, }

    if reward_points is None:
        error_message = "You don't have enough reward points to redeem this reward."
        return render(request, 'error.html', context)
    elif reward_points.points >= reward.points_required:
            reward_points.points -= reward.points_required
            reward_points.save()
            return redirect('index')
    else:
        error_message = "You don't have enough reward points to redeem this reward."
        context = {
            'error_message': error_message,}

        return render(request, 'error.html', context)

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
def like_post_details(request, post_id):
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
    return redirect('post_detail', post_id=post.id)

@login_required
def like_reply(request, reply_id, post_id):
    reply = get_object_or_404(Reply, id=reply_id)
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    content_type = ContentType.objects.get_for_model(Reply)
    try:
        like = Like.objects.get(
            content_type=content_type,
            object_id=reply_id,
            user=user,
        )
        like.delete()
        created = False
    except Like.DoesNotExist:
        like = Like.objects.create(
            content_type=content_type,
            object_id=reply_id,
            user=user,
        )
        created = True
    like_count = reply.likes.count()
    return redirect('post_detail', post_id=post.id)

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

