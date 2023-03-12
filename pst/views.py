from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from django.contrib.auth.decorators import login_required
from django.contrib import auth

from django.urls import reverse
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from pst.forms import CategoriesForm, AddSpendingForm, LoginForm, EditProfileForm, PostForm, ReplyForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

import calendar
from datetime import date, datetime

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


# Create your views here.


@login_required
def user_feed(request):
    return render(request, 'user_feed.html')


@login_prohibited
def visitor_signup(request):
    if request.method == 'POST':
        form = VisitorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user,
                       backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        else:
            return render(request, 'visitor_signup.html', {'form': form})
    else:
        form = VisitorSignupForm()
        return render(request, 'visitor_signup.html', {'form': form})


#Create a calendar which shows the sum of expenditures and incomes of all spendings of each day in a month
def get_spending_calendar_context(request, year=datetime.now().year, month=datetime.now().month):
    month_calendar = calendar.Calendar()
    month_calendar_list = month_calendar.monthdays2calendar(year,month)
    month_name = calendar.month_name[month]
    spendings = Spending.objects.all()
    if month==1:
        previous_month = 12
        previous_year = year - 1
        next_month = 2
        next_year = year
    elif month ==12:
        previous_month = 11
        previous_year = year
        next_month = 1
        next_year = year + 1
    else:
        previous_month = month - 1
        next_month = month + 1
        next_year = year
        previous_year = year

    for i in range(0, len(month_calendar_list)):
        for j in range(0, len(month_calendar_list[i])):
            spendings_daily = []
            exp_sum = 0
            income_sum = 0
            #adds each spending in the database to each date in the calendar
            for spending in spendings:
                if spending.date.day == month_calendar_list[i][j][0] and spending.date.month == month and spending.date.year == year:
                    spendings_daily.append(spending)
            #calculates the sum of expenditures and sums of all the spendings in a single day
            for spending_daily in spendings_daily:
                if spending_daily.spending_type == Spending_type.EXPENDITURE:
                    exp_sum += spending_daily.amount
                else:
                    income_sum += spending_daily.amount
            month_calendar_list[i][j] = (month_calendar_list[i][j][0], month_calendar_list[i][j][1], exp_sum, income_sum)

    context = {'month_calendar_list': month_calendar_list,
               'year': year, 'month': month_name, 
               'previous_month': previous_month, 
               'previous_year': previous_year, 
               'next_month': next_month, 
               'next_year': next_year,
               'exp_amount': exp_sum,
               'income_amount': income_sum}
    return context

@login_required
def home(request):
    user = request.user
    percentage = calculate_budget(request)
    month=datetime.now().month
    revenue = Spending.objects.filter(
        spending_owner=request.user,
        date__month=month,
        spending_type=Spending_type.INCOME,
    )

    if (not revenue):
        monthly_revenue = 0
    else:
        monthly_revenue = revenue.aggregate(nums=Sum('amount')).get('nums')

    expense = Spending.objects.filter(
        spending_owner=request.user,
        date__month=month,
        spending_type=Spending_type.EXPENDITURE,
    )

    if (not expense):
        monthly_expense = 0
    else:
        monthly_expense = expense.aggregate(nums=Sum('amount')).get('nums')

    
    context = {'user': user, 'percentage': percentage,
               'revenue': monthly_revenue, 'expense': monthly_expense, 'month_in_number': month}
    
    calendar_context = get_spending_calendar_context(request)

    context.update(calendar_context)
               

    return render(request, 'home.html', context)

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
                next = request.GET.get('next') or ''
                redirect_url = next or 'home'
                return redirect(redirect_url)

        else:
            messages.add_message(request, messages.ERROR,
                                 "The credentials provided are invalid!")

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
        "finance": ["With the PST, you can take control of your personal finances and make informed decisions about your spending and saving."],
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



def get_categories_by_type(request):
    spending_type = request.GET.get('spending_type', '')
    categories = Categories.objects.filter(
        owner=request.user,
        categories_type=spending_type
    ).values('id', 'name')

    data = {
        'categories': list(categories)
    }
    return JsonResponse(data)


@login_required
def view_spendings(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        spending = Spending.objects.filter(spending_owner=request.user,
                                           date__range=[start_date, end_date]).order_by('date')
    else:
        spending = Spending.objects.filter(
            spending_owner=request.user).order_by('date')

    paginator = Paginator(spending, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = EditSpendingForm(user=request.user)
    context = {'form': form, 'spending': spending, 'page_obj': page_obj}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'spending_table.html', context)
    else:
        return render(request, 'view_spendings.html', context)


@login_required
def edit_spending(request, spending_id):
    try:
        spending = Spending.objects.get(id=spending_id)
    except ObjectDoesNotExist:
        return render(request, 'view_spendings.html')

    if request.method == 'POST':
        form = EditSpendingForm(request.user, request.POST, instance=spending)

        if form.is_valid():
            form.save()
            messages.success(request, 'Change made successfully')
            return redirect('view_spendings')
    else:
        form = EditSpendingForm(user=request.user)
    return redirect('view_spendings')


@login_required
def delete_spending(request, spending_id):

    delete_spending = get_object_or_404(Spending, id=spending_id)
    delete_spending.delete()
    messages.warning(request, "spending has been deleted")
    return redirect('view_spendings')


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
            return redirect('view_spendings')
    else:
        form = AddSpendingForm()
    return render(request, 'view_spendings.html',  {'form': form})


@login_required
def add_spending_categories(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.owner = request.user
            category.save()
            return redirect('view_spending_categories')
    else:
        form = CategoriesForm()
    return render(request, 'view_spending_categories.html',  {'form': form})


@login_required
def view_spending_categories(request):
    form = CategoriesForm()
    categories_expenditure = Categories.objects.filter(
        categories_type=Spending_type.EXPENDITURE, owner=request.user)
    categories_income = Categories.objects.filter(
        categories_type=Spending_type.INCOME, owner=request.user)
    return render(request, 'view_spending_categories.html', {'categories_expenditure': categories_expenditure, 'categories_income': categories_income, 'form': form})


@login_required
def delete_spending_categories(request, category_id):
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
                messages.success(request, 'Change made successfully')
                return redirect('view_spending_categories')
        else:
            messages.add_message(request, messages.ERROR,
                                 "You can not modify default category!")
            return redirect('view_spending_categories')
    else:
        category = Categories.objects.get(id=category_id)
        form = CategoriesForm(instance=category)
    return redirect('view_spending_categories')


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
def spending_report(request):
    expenditures = Spending.objects.filter(
        spending_type=Spending_type.EXPENDITURE)
    expenditures_data = expenditures.values(
        'spending_category__name').annotate(exp_amount=Sum('amount'))
    return render(request, 'spending_report.html', {'expenditures': expenditures, 'expenditures_data': expenditures_data})

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


def calculate_budget(request):
    total = Spending.objects.aggregate(nums=Sum('amount')).get('nums')
    budget = Budget.objects.filter(budget_owner=request.user).last()
    if budget == None:
        spending_percentage = 0
    elif total == None:
        spending_percentage = 0
    else:
        spending_percentage = int((total / budget.limit) * 100)
    return spending_percentage


@login_required
def show_budget(request):
    budget = Budget.objects.filter(budget_owner=request.user).last()
    percentage = calculate_budget(request)

    # check if a message with the INFO level already exists
    message_exists = False
    for message in messages.get_messages(request):
        if message.level == messages.INFO:
            message_exists = True
            break

    if percentage >= 100 and not message_exists:
        messages.add_message(request, messages.INFO,
                             'you have exceeded the limit')

    form = BudgetForm()

    return render(request, 'budget_show.html', {'budget': budget, 'spending_percentage': percentage, 'form': form})


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
            'error_message': error_message, }

        return render(request, 'error.html', context)


@login_required
def forum(request):
    posts = Post.objects.all().order_by('-post_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for post in page_obj:
        post.replies = Reply.objects.filter(parent_post=post)

    return render(request, 'forum.html', {'page_obj': page_obj})


@login_required
def personal_forum(request):
    posts = Post.objects.filter(user=request.user).order_by('-post_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for post in page_obj:
        post.replies = Reply.objects.filter(parent_post=post)

    reply_page_number = request.GET.get('reply_page')
    replies = Reply.objects.filter(user=request.user).order_by('-reply_date')
    reply_paginator = Paginator(replies, 5)
    reply_page_obj = reply_paginator.get_page(reply_page_number)

    return render(request, 'personal_forum.html', {'page_obj': page_obj, 'reply_page_obj': reply_page_obj})


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            for file in request.FILES.getlist('image'):
                PostImage.objects.create(
                    post=post,
                    image=file
                )
            return redirect('forum')
    else:
        form = PostForm()
    return render(request, 'add_post.html',  {'form': form})


@login_required
def post_detail(request, post_id):
    #post = get_object_or_404(Post, id=post_id)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponseNotFound()
    replies = Reply.objects.filter(parent_post=post)
    paginator = Paginator(replies, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'post': post, 'replies': replies, 'page_obj': page_obj}
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

    return redirect(request.META.get('HTTP_REFERER', reverse('forum')))


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

    redirect_url = request.META.get(
        'HTTP_REFERER', reverse('post_detail', args=[post_id]))
    return redirect(redirect_url)


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
    redirect_url = request.META.get(
        'HTTP_REFERER', reverse('post_detail', args=[post_id]))
    return redirect(redirect_url)


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


@login_required
def add_reply_to_reply(request, post_id, parent_reply_id):
    post = get_object_or_404(Post, id=post_id)
    parent_reply = get_object_or_404(Reply, id=parent_reply_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.parent_post = post
            reply.parent_reply = parent_reply
            reply.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = ReplyForm()

    context = {'form': form, 'post': post, 'parent_reply': parent_reply}
    return render(request, 'add_reply_to_reply.html', context)


@login_required
def view_post_user(request, user_id, post_id):
    user = User.objects.get(id=user_id)
    post = Post.objects.get(id=post_id)
    context = {'user': user, 'post': post}
    return render(request, 'view_post_user.html', context)


@login_required
def view_settings(request):
    form = BudgetForm()
    return render(request, 'setting_page.html', {'form': form})

@login_required
# Create a calendar which shows the sum of expenditures and incomes of all spendings of each day in a month
def spending_calendar(request, year=datetime.now().year, month=datetime.now().month):
    context = get_spending_calendar_context(request, year, month)   
    return render(request, 'spending_calendar.html', context)