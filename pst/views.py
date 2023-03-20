from audioop import reverse
import datetime
from django.db.models import Sum
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from django.contrib.auth.decorators import login_required
from django.contrib import auth

from django.urls import reverse
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from pst.forms import CategoriesForm, AddSpendingForm, LoginForm, EditProfileForm, PostForm, ReplyForm
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from django.db.models import Max, Sum, Subquery, OuterRef

import calendar
from datetime import date, datetime
import datetime as dt

from .models import User, Categories, Spending, SpendingFile, Reward, Budget, SpendingFile, PostImage, Like, DailyTask, DailyTaskStatus, Day, TaskType, DeliveryAddress

from .forms import *
from django.views import View
from django.utils.decorators import method_decorator
from pst.helpers.auth import login_prohibited
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password

import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings
from NewHappy.settings import MEDIA_ROOT
from django.http import HttpResponse
import random
import nltk
nltk.download('punkt')
nltk.download('wordnet')



high_task_points = 30
normal_task_points = 10
current_datetime = timezone.now()

@login_required
def user_feed(request):
    return render(request, 'user_feed.html')


@login_prohibited
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


# Create a calendar which shows the sum of expenditures and incomes of all spendings of each day in a month
def get_spending_calendar_context(request, year=datetime.now().year, month=datetime.now().month):
    month_calendar = calendar.Calendar()
    month_calendar_list = month_calendar.monthdays2calendar(year, month)
    month_name = calendar.month_name[month]
    spendings = Spending.objects.filter(spending_owner=request.user)
    if month == 1:
        previous_month = 12
        previous_year = year - 1
        next_month = 2
        next_year = year
    elif month == 12:
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
            # adds each spending in the database to each date in the calendar
            for spending in spendings:
                if spending.date.day == month_calendar_list[i][j][0] and spending.date.month == month and spending.date.year == year:
                    spendings_daily.append(spending)
            # calculates the sum of expenditures and sums of all the spendings in a single day
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

def get_login_task_status(request):
    pos = int(request.GET.get("pos", 0))
    task_statuses  = DailyTaskStatus.objects.filter(
    day__number__lte=pos,
    task_type=TaskType.LOGIN.name,
    task__user=request.user,

    )

    # Create a dictionary with day numbers as keys and completed status as values
    task_status_dict = {
        task_status.day.number: True
        for task_status in task_statuses
    }

    # Create a list of dictionaries for each day from 1 to pos, with their completion status
    data = {
        "task_statuses": [
            {
                "day": day,
                "completed": task_status_dict.get(day, False),
            }
            for day in range(1, pos + 1)
        ]
    }

    if not task_status_dict.get(pos) and len(data['task_statuses']) > 0:
        data['task_statuses'].pop()

    return JsonResponse(data)

@login_required
@csrf_exempt
def add_login_task_points(request):
    if request.method == 'POST':

        user = request.user
        login_task = DailyTask.objects.create(user=user)
        current_day = get_number_days_from_register(request)
        day, _ = Day.objects.get_or_create(number=current_day)
        print(day)
        # give user extra points if user has login consecutive for seven days
        if user.consecutive_login_days > 7:
            daily_task_status = DailyTaskStatus.objects.create(
                task=login_task,
                day=day,
                task_points=high_task_points,
                task_type=TaskType.LOGIN.name
            )

        else:

            daily_task_status = DailyTaskStatus.objects.create(
                task=login_task,
                day=day,
                task_points=normal_task_points,
                task_type=TaskType.LOGIN.name
            )



        return JsonResponse({"status": "success"})


def check_already_logged_in_once_daily(request):
    user = request.user
    # if over a day since last login
    if current_datetime - user.last_login > timedelta(hours=24):
        user.logged_in_once_daily = False
        user.save()
    else:
        user.logged_in_once_daily = True
        user.save()


def get_number_days_from_register(request):
    date_joined = request.user.date_joined
    num_days = (current_datetime - date_joined).days + 1
    if  num_days == 0:
        num_days = 1

    return num_days


def get_position_in_daily_reward(request):
    pos = get_number_days_from_register(request)
    return pos % 35


def get_super_task_point_position(request):
    consecutive_login_days = request.user.consecutive_login_days
    cur_pos = get_position_in_daily_reward(request)
    days_need = 7 - consecutive_login_days
    return cur_pos + days_need


def add_consecutive_login_days(request):
    user = request.user
    if current_datetime - user.last_login < timedelta(hours=24) and user.logged_in_once_daily == False:
        user.consecutive_login_days += 1

        # user has not logged in consecutively
    elif current_datetime - user.last_login >= timedelta(hours=24):
        user.consecutive_login_days = 1
    user.save()



@login_required
def home(request):
    week_list = [1,2,3,4,5]
    weekday_list = [1,2,3,4,5,6,7]
    current_day = str(timezone.now().day)
    pos = get_position_in_daily_reward(request)
    super_task_pos = get_super_task_point_position(request)

    user = request.user
    percentage = calculate_budget(request)
    month = datetime.now().month
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

    daily_reward_context = {"pos": pos, "super_task_pos": super_task_pos, "week_list": week_list,
                            "weekday_list": weekday_list, "current_datetime": current_day,
                            "high_task_points": high_task_points, "normal_task_points": normal_task_points}

    calendar_context = get_spending_calendar_context(request)

    context.update(calendar_context)
    context.update(daily_reward_context)

    return render(request, 'home.html', context)


@login_prohibited
def visitor_introduction(request):
    return render(request, 'visitor_introduction.html')



@login_required
def edit_spending(request, spending_id):
    # if request.method == 'POST':
    #     form = EditSpendingForm(request.POST)
    #     if form.is_valid():
    try:
        spending = Spending.objects.get(id = spending_id)
    except ObjectDoesNotExist:
        return render(request, 'view_spendings.html')

    if request.method == 'POST':
        form = EditSpendingForm(request.POST, instance=spending)
        if form.is_valid():
            form.save()
            request.spending.save()
            messages.success(request, 'success')
            return redirect('view_spendings')
    else:
        form = EditSpendingForm(instance=spending)
    return render(request, "edit_spending.html", {'form': form, 'spending': spending})


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
                next = request.GET.get('next') or ''
                add_consecutive_login_days(request)
                check_already_logged_in_once_daily(request)
                user.last_login = timezone.now()
                user.save()

                return redirect(redirect_url)

            else:
                messages.add_message(request, messages.ERROR, "The credentials provided are invalid!")



    form = LoginForm()

    return render(request, 'log_in.html', {'form': form})



def log_out(request):
    logout(request)
    return redirect('visitor_introduction')


# Chatbot is a simple virtual help assistant that can answer user's question base on keywords
@login_required
def chat_bot(request):
    chat_history = []  # this is use to store all the chat history between user and chatbot
    if request.method == 'POST':
        user_input = request.POST['user_input']
        chat_bot_response = respond(request, user_input)
        chat_history.append((user_input, chat_bot_response))
        return render(request, 'chat_bot.html', {'chat_history': chat_history})
    return render(request, 'chat_bot.html', {'chat_history': chat_history})

@login_required
def respond(request, user_input):
    lemmatizer = WordNetLemmatizer()
    keywords = {
        "pst": ["personal spending tracker", "pst"],
        "category": ["category", "categories", "spending category"],
        "budget": ["budget", "spending budget", "financial budget", "myplan"],
        "expense": ["expense", "spending", "financial expense"],
        "track": ["track", "record", "keep track"],
        "forum": ["forum", "discussion board", "message board", "online community", "bulletin board", "chat room"],
        "report": ["report", "chart"],
        "reward": ["reward", "shop", "points"],
        "calender": ["calender", "date"],

        "help": ["help"],
        "hello": ["hi", "hello", "hey", "greetings", "heya", "hola", "what's up", "sup"],
        "bye": ["bye", "goodbye", "see you later", "adios", "later", "farewell"]
    }

    responses = {
        "pst": ["Our Personal Spending Tracker helps you keep track of your daily expenses and budget."],
        "category": [
            "While we offer default categories for both income and expenses, you always have the option to customize them to fit your personal preferences and needs in the settings!"],
        "budget": ["You can use our Personal Spending Tracker to set budgets for different categories of expenses."],
        "expense": [
            "You can log all your expenses on our Personal Spending Tracker, including the date, category, and amount spent."],
        "track": [
            "Our Personal Spending Tracker is designed to help you keep track of your daily expenses, budget, and savings."],
        "forum": [
            "Our online forum is a great place to connect with other users, share tips and advice, and discuss personal finance topics. You can join the forum by simply clicking on the Forum button on the home page."],
        "report": [
            "Our report feature can create a chart of your expenses and provide a detailed list of your spending."],
        "reward": [
            "By using our Personal Spending Tracker consistently, you can earn points which can be redeemed for various rewards in our reward shop."],
        "calender": [
            "Our calendar feature can assist you in monitoring your income and expenses for the current month, allowing you to quickly determine your spending and effectively manage your financial plan with greater efficiency!"],

        "help": [
            "you can try asking about pst, budget, expense, track, forum, report, rewards, category, calender for more information."],
        "hello": ["Hello! How may I help you?"],
        "bye": ["Goodbye! Have a great day!"],
    }
    if user_input:
        for keyword, synonyms in keywords.items():
            if user_input.lower() in [s.lower() for s in synonyms]:
                return random.choice(responses[keyword])

        tokens = word_tokenize(user_input)
        tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]

        possible_keywords = []
        for keyword, synonyms in keywords.items():
            for token in tokens:
                if token in synonyms:
                    possible_keywords.append(keyword)
                    break

        if possible_keywords:
            message = f"Did you mean {', '.join(possible_keywords)}?"
        else:
            message = "Sorry, I do not understand what you mean. You can type 'help' for a list of possible commands."

        for keyword in possible_keywords:
            if keyword in responses:
                message = random.choice(responses[keyword])
                break

        return message
    else:
        messages.add_message(request, messages.ERROR,
                             "You can not submit empty space!!!")

@login_required
def view_spendings(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_sort = request.GET.get('sorted')

    if start_date and end_date:
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
        unsorted_spending = Spending.objects.filter(spending_owner=request.user,
                                           date__range=[start_date, end_date]).order_by('-date')
    else:
        unsorted_spending = Spending.objects.filter(
            spending_owner=request.user).order_by('-date')

    if selected_sort == 'Income':
        spending = unsorted_spending.filter(spending_type=Spending_type.INCOME)
    elif selected_sort == 'Expenditure':
        spending = unsorted_spending.filter(spending_type=Spending_type.EXPENDITURE)
    elif selected_sort:
        spending = unsorted_spending.order_by(selected_sort)
    else:
        spending = unsorted_spending

    paginator = Paginator(spending, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    add_form = AddSpendingForm(user=request.user)
    edit_form = EditSpendingForm(user=request.user)
    context = {'add_form': add_form, 'edit_form': edit_form, 'spending': spending, 'page_obj': page_obj}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'spending_table.html', context)
    else:
        return render(request, 'view_spendings.html', context)


@login_required
def edit_spending(request, spending_id):
    try:
        spending = Spending.objects.get(id = spending_id)
    except ObjectDoesNotExist:
        return redirect('view_spendings')
        

    if request.method == 'POST':
        form = EditSpendingForm(
            request.user, request.POST, request.FILES, instance=spending)
        
        if form.is_valid():
            form.save()
            file_list = request.FILES.getlist('file')
            if file_list:
                SpendingFile.objects.filter(spending=spending).delete()
                for file in file_list:
                    SpendingFile.objects.create(
                        spending=spending,
                        file=file
                    )
            if form.cleaned_data['delete_file']:
                SpendingFile.objects.filter(spending=spending).delete()
            messages.success(request, 'Change made successfully')
            return redirect('view_spendings')
    else:
        form = EditSpendingForm(user=request.user)
    return render(request, "edit_spending.html", {'form': form, 'spending': spending})


@login_required
def delete_spending(request, spending_id):

    delete_spending = get_object_or_404(Spending, id = spending_id)
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
            messages.success(request, 'Spending added successfully')
            return redirect('view_spendings')
    else:
        form = AddSpendingForm()
    return render(request, 'view_spendings.html', {'form': form})


@login_required
def add_spending_categories(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.owner = request.user
            category.save()
            messages.add_message(request, messages.SUCCESS,
                             "Category successfully added")
            return redirect('view_spending_categories')

    else:
        form = CategoriesForm()
    return render(request, 'view_spending_categories.html', {'form': form})

@login_required
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
def view_spending_categories(request):
    form = CategoriesForm()
    categories_expenditure = Categories.objects.filter(
        categories_type=Spending_type.EXPENDITURE, owner=request.user)
    categories_income = Categories.objects.filter(
        categories_type=Spending_type.INCOME, owner=request.user)
    return render(request, 'view_spending_categories.html',
                  {'categories_expenditure': categories_expenditure, 'categories_income': categories_income,
                   'form': form})


@login_required
def delete_spending_categories(request, category_id):
    category = Categories.objects.get(id=category_id)
    if category.default_category == False:
        category.delete()
        messages.add_message(request, messages.SUCCESS,
                             "Category successfully deleted")
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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_categories = request.GET.get('selected_categories')
    sorted = request.GET.get('sorted')
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        spendings = Spending.objects.filter(spending_owner=request.user, date__range=[start_date, end_date])
    else:
        spendings = Spending.objects.filter(spending_owner=request.user)

    if selected_categories == 'Income':
        report_type = 'Income'
        selected_spendings = spendings.filter(spending_type=Spending_type.INCOME)
    else:
        report_type = 'Expenditure'
        selected_spendings = spendings.filter(spending_type=Spending_type.EXPENDITURE)
    spendings_data = selected_spendings.values('spending_category__name').annotate(exp_amount=Sum('amount'))

    if sorted == 'spending_category':
        sorted_spendings = selected_spendings.order_by('spending_category')
    elif sorted == 'amount':
        sorted_spendings = selected_spendings.order_by('amount')
    elif sorted == '-amount':
        sorted_spendings = selected_spendings.order_by('-amount')
    elif sorted == 'date':
        sorted_spendings = selected_spendings.order_by('date')
    else:
        sorted_spendings = selected_spendings

    paginator = Paginator(sorted_spendings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'report_type': report_type,
        'selected_spendings': selected_spendings,
        'spendings_data': spendings_data,
        'sorted': sorted,
        'sorted_spendings': sorted_spendings,
        'page_obj': page_obj
        }
    return render(request, 'spending_report.html', context)

@login_required
def set_budget(request):
    if request.method == 'POST':
        form = TotalBudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.budget_owner = request.user
            budget.save()
            return redirect('budget_show')
    else:
        form = TotalBudgetForm(request.user)
    return render(request, 'budget_set.html', {'form': form})


def calculate_budget(request):
    # budget = sum(category_budgets.values_list('total_budget', flat=True))
    budget = TotalBudget.objects.filter(budget_owner=request.user).last()
    if budget:
        total = Spending.objects.filter(
            spending_owner=request.user,
            spending_type=Spending_type.EXPENDITURE,
            date__range=(budget.start_date, budget.end_date),
        ).aggregate(
            nums=Sum('amount')
        ).get('nums') or 0
    else:
        total = 0
    if budget == None:
        spending_percentage = 0
    elif total == None:
        spending_percentage = 0
    else:
        spending_percentage = int((total / budget.limit) * 100)
    return spending_percentage


@login_required
def show_budget(request):
    selected_sort = request.GET.get('sorted')
    # the budget will be refreshed automatically after the end date
    # of your last budget
    create_new_budget_if_needed(request)
    # current_month = datetime.now().month
    total_budget = TotalBudget.objects.filter(budget_owner=request.user).last()
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

    # the budget will be refreshed automatically after the end date
    # of your last budget
    category_budgets = get_category_budgets(request, total_budget)
    sorted_category_budgets = sort_catrgory_budget(request, selected_sort, category_budgets)
    form = TotalBudgetForm(request.user)
    specific_form = BudgetForm(request.user)

    return render(request, 'budget_show.html', {
        'budget': total_budget,
        'spending_percentage': percentage,
        'category_budgets': sorted_category_budgets,
        'form': form,
        'specific_form': specific_form,
    })


# @login_required
# def index(request):
#     if Reward.objects.count() == 0:
#         Reward.objects.create(name='Discount coupon', points_required=10)
#         Reward.objects.create(name='Free T-shirt', points_required=20)
#         Reward.objects.create(name='Gift card', points_required=50)



@login_required
def index(request):
    address = DeliveryAddress.objects.filter(user=request.user).last()
    form = AddressForm(instance=address)

    if Reward.objects.count() == 0:
        Reward.objects.create(
            name='T-shirt', points_required=10, image='rewards/shirt.jpg')
        Reward.objects.create(name='PSN £50 Gift Card',
                              points_required=500, image='rewards/playstation_gift_card.jpg')
        Reward.objects.create(name="XBX £10 Gift Card",
                              points_required=100, image='rewards/xbox_gift_card.jpg')
        Reward.objects.create(name="AMZ £20 Gift Card",
                              points_required=200, image='rewards/amazon_gift_card.jpg')

#
    rewards = Reward.objects.all()
    context = {
        'form': form,
        'rewards': rewards,
        'task_points': request.user.total_task_points,
        'address': address,
    }
    return render(request, 'index.html', context)


@login_required
def redeem(request, reward_id):
    user = request.user
    total_task_points = user.total_task_points
    reward = Reward.objects.get(id=reward_id)

    if total_task_points is None:

        messages.add_message(
            request, messages.INFO, "You don't have enough reward points to redeem this reward.")
        return redirect('index')
    elif total_task_points >= reward.points_required:
        user.decrease_total_task_points(reward.points_required)
        messages.add_message(
            request, messages.INFO, 'Successfully redeemed, your item will be shipped to your address within 7 days.')
        return redirect('index')
    else:

        messages.add_message(
            request, messages.INFO, "You don't have enough reward points to redeem this reward.")
        return redirect('index')


def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'success')
            return redirect('index')

    else:
        form = AddressForm()
    return render(request, "index.html", {'form': form})


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

    return render(request, 'personal_forum.html', {'page_obj': page_obj})


@login_required
def personal_forum_reply(request):
    reply_page_number = request.GET.get('reply_page')
    replies = Reply.objects.filter(user=request.user).order_by('-reply_date')
    reply_paginator = Paginator(replies, 5)
    reply_page_obj = reply_paginator.get_page(reply_page_number)

    return render(request, 'personal_forum_reply.html', {'reply_page_obj': reply_page_obj})


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
                    file=file
                )
            return redirect('forum')
    else:
        form = PostForm()
    return render(request, 'add_post.html',  {'form': form})

@login_required
def delete_post(request, post_id):

    delete_post = get_object_or_404(Post, id=post_id)
    delete_post.delete()
    messages.warning(request, "post has been deleted")
    return redirect('personal_forum')


@login_required
def post_detail(request, post_id):
    #post = get_object_or_404(Post, id=post_id)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponseNotFound()
    replies = Reply.objects.filter(parent_post=post)
    paginator = Paginator(replies, 4)
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
def delete_reply(request, reply_id):

    delete_reply = get_object_or_404(Reply, id=reply_id)
    delete_reply.delete()
    messages.warning(request, "reply has been deleted")
    return redirect('personal_forum_reply')


@login_required
def view_post_user(request, user_id, post_id):
    user = User.objects.get(id=user_id)
    post = Post.objects.get(id=post_id)
    context = {'user': user, 'post': post}
    return render(request, 'view_post_user.html', context)


@login_required
def view_settings(request):
    form = TotalBudgetForm(request.user)
    return render(request, 'setting_page.html', {'form': form})


@login_required
# Create a calendar which shows the sum of expenditures and incomes of all spendings of each day in a month
def spending_calendar(request, year=datetime.now().year, month=datetime.now().month):
    context = get_spending_calendar_context(request, year, month)
    return render(request, 'spending_calendar.html', context)

@login_required
def set_specific_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.budget_owner = request.user
            budget.save()
            return redirect('budget_show')
    else:
        form = BudgetForm(request.user)
    return render(request, 'specific_budget_set.html', {'form': form})

@login_required
def password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = PasswordForm(data=request.POST)
            if form.is_valid():
                password = form.cleaned_data.get('password')
                if check_password(password, current_user.password):
                    new_password = form.cleaned_data.get('new_password')
                    current_user.set_password(new_password)
                    current_user.save()
                    authenticated_user = authenticate(username=current_user.username, password=new_password)
                    login(request, authenticated_user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.add_message(request, messages.SUCCESS, "Password updated!")
                    return redirect('password')
                else:
                    messages.add_message(request, messages.ERROR, "Make sure you input right current password.")

            else:
                messages.add_message(request, messages.ERROR, "Please ensure that you enter the same password twice, and it contains at least one uppercase letter, one lowercase letter, and one number.")

        form = PasswordForm()
        return render(request, 'password.html', {'form': form})

@login_required
def create_new_budget_if_needed(request):
    current_budget = TotalBudget.objects.filter(budget_owner=request.user).last()
    if current_budget and current_budget.end_date < datetime.now().date():
        TotalBudget.objects.create(
            limit=current_budget.limit,
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=30),
            budget_owner=request.user,
        )

@login_required
def get_category_budgets(request, total_budget):
    categories = Categories.objects.filter(owner=request.user, categories_type=Spending_type.EXPENDITURE)
    category_budgets = []
    for category in categories:
        budget = Budget.objects.filter(spending_category=category).last()
        if budget:
            # print(category.name + str(budget.limit))
            spending_sum = Spending.objects.filter(
                spending_owner=request.user,
                # date__month=current_month,
                date__range=(total_budget.start_date, total_budget.end_date),
                spending_type=Spending_type.EXPENDITURE,
                spending_category=category,
            ).aggregate(nums=Sum('amount')).get('nums') or 0

            # print(budget.limit)
            category_budgets.append({
                'name': category.name,
                'budget': budget.limit,
                'spending': spending_sum,
                'percentage': int(spending_sum / budget.limit * 100) if budget.limit else None,
                # 'start_date': total_budget.start_date,
                # 'end_date': total_budget.end_date,
            })
        else:
            if total_budget:
                spending_sum = Spending.objects.filter(spending_owner=request.user,
                                                       date__range=(total_budget.start_date, total_budget.end_date),
                                                       spending_type=Spending_type.EXPENDITURE,
                                                       spending_category=category,
                                                       ).aggregate(nums=Sum('amount')).get('nums') or 0
                category_budgets.append({
                    'name': category.name,
                    'budget': 'Not set yet',
                    'spending': spending_sum,
                    'percentage': None,
                    # 'start_date': None,
                    # 'end_date': None,
                })
            else:
                category_budgets.append(
                    {'name': category.name, 'budget': 'Not set yet', 'spending': 'Please set a total budget first',
                     'percentage': None,
                     })
    return category_budgets

@login_required
def sort_catrgory_budget(request, selected_sort, category_budgets):
    if selected_sort == '-budget':
        sorted_category_budgets = sorted(
            category_budgets,
            key=lambda k: (
                k['budget'] != 'Not set yet',
                float(k['budget']) if isinstance(k['budget'], str) and k['budget'] != 'Not set yet' else k['budget']
            ),
            reverse=True
        )
    elif selected_sort == 'budget':
        sorted_category_budgets = sorted(
            category_budgets,
            key=lambda k: (
                k['budget'] != 'Not set yet',
                float(k['budget']) if isinstance(k['budget'], str) and k['budget'] != 'Not set yet' else k['budget']
            )
        )
    elif selected_sort == '-spending':
        sorted_category_budgets = sorted(
            category_budgets,
            key=lambda k: (
                k['spending'] != 'Please set a total budget first',
                float(k['spending']) if isinstance(k['spending'], str) and k['spending'] != 'Please set a total budget first' else k['spending']
            ),
            reverse=True
        )
    elif selected_sort == 'spending':
        sorted_category_budgets = sorted(
            category_budgets,
            key=lambda k: (
                k['spending'] != 'Please set a total budget first',
                float(k['spending']) if isinstance(k['spending'], str) and k['spending'] != 'Please set a total budget first' else k['spending']
            ),
        )
    elif selected_sort == '':
        sorted_category_budgets = category_budgets
    else:
        sorted_category_budgets = category_budgets
    return sorted_category_budgets