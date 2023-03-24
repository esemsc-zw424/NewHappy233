from audioop import reverse
import datetime
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from django.contrib import auth

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

import calendar
from datetime import datetime
import datetime as dt

from .models import Reward, PostImage, Like, DailyTask, DailyTaskStatus, Day, TaskType

from .forms import *
from django.views import View
from pst.helpers.auth import login_prohibited
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password

from django.conf import settings
import random
import nltk
nltk.download('punkt')
nltk.download('wordnet')




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
               'year': year, 
               'month': month_name,
               'previous_month': previous_month,
               'previous_year': previous_year,
               'next_month': next_month,
               'next_year': next_year,
               'exp_amount': exp_sum,
               'income_amount': income_sum}
    return context


class GetLoginTaskStatusView(View):
    
    def get(self, request):
        pos = self.get_position(request)
        task_statuses = self.get_task_statuses(request, pos)
        task_status_dict = self.build_task_status_dict(task_statuses)
        data = self.build_data(pos, task_status_dict)
        return JsonResponse(data)
    

    def get_position(self, request):
        return int(request.GET.get("pos", 0))
    

    def get_task_statuses(self, request, pos):
        return DailyTaskStatus.objects.filter(
            day__number__lte=pos,
            task_type=TaskType.LOGIN.name,
            task__user=request.user,
        )
    

    def build_task_status_dict(self, task_statuses):
        return {task_status.day.number: True for task_status in task_statuses}
    

    def build_data(self, pos, task_status_dict):
        task_statuses = [
            {"day": day, "completed": task_status_dict.get(day, False)}
            for day in range(1, pos + 1)
        ]
        if not task_status_dict.get(pos) and len(task_statuses) > 0:
            task_statuses.pop()
        return {"task_statuses": task_statuses}
    
    

    
def add_login_task_points(request):
    if request.method == 'POST':
        user = request.user
        login_task = create_login_task(user)
        create_daily_task_status(request, login_task)
        return JsonResponse({"status": "success"})
    

def create_login_task(user):
    return DailyTask.objects.create(user=user)


def create_daily_task_status(request, login_task):
    current_day = request.user.get_number_days_from_register()
    day, _ = Day.objects.get_or_create(number=current_day)
    if request.user.consecutive_login_days > 7:
        task_points = settings.HIGH_TASK_POINTS
    else:
        task_points = settings.NORMAL_TASK_POINTS
    return DailyTaskStatus.objects.create(
        task=login_task,
        day=day,
        task_points=task_points,
        task_type=TaskType.LOGIN.name
    )   



def get_position_in_daily_reward(request):
    pos = request.user.get_number_days_from_register()
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
        monthly_revenue = round(revenue.aggregate(nums=Sum('amount')).get('nums'), 2)

    expense = Spending.objects.filter(
        spending_owner=request.user,
        date__month=month,
        spending_type=Spending_type.EXPENDITURE,
    )

    if (not expense):
        monthly_expense = 0
    else:
        monthly_expense = round(expense.aggregate(nums=Sum('amount')).get('nums'), 2)

    context = {'user': user, 'percentage': percentage,
               'revenue': monthly_revenue, 'expense': monthly_expense, 'month_in_number': month}

    daily_reward_context = {"pos": pos, "super_task_pos": super_task_pos, "week_list": week_list,
                            "weekday_list": weekday_list, "current_datetime": current_day,
                            "high_task_points": settings.HIGH_TASK_POINTS, "normal_task_points": settings.NORMAL_TASK_POINTS}

    calendar_context = get_spending_calendar_context(request)

    context.update(calendar_context)
    context.update(daily_reward_context)

    return render(request, 'home.html', context)


@login_prohibited
def visitor_introduction(request):
    return render(request, 'visitor_introduction.html')



@login_required
def edit_spending(request, spending_id):
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
                user.check_already_logged_in_once_daily()
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
# User can type in some quesiton, and by identifing key words in the question, chatbot can provide user with relevant answer
@login_required
def chat_bot(request):
    chat_history = []  # this is use to store response from chatbot and print it out in the web
    if request.method == 'POST':
        user_input = request.POST['user_input']
        chat_bot_response = respond(request, user_input)
        chat_history.append((user_input, chat_bot_response))
        return render(request, 'chat_bot.html', {'chat_history': chat_history})
    return render(request, 'chat_bot.html', {'chat_history': chat_history})

# This function receives user input and responds with pre-defined messages based on identified keywords or phrases
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

    # The keyword can still be identify no matter it is in capital letter or lower letter
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

    # retrieve spending in given time interval if user specified start date and end date
    if start_date and end_date:
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
        unsorted_spending = Spending.objects.filter(spending_owner=request.user,
                                           date__range=[start_date, end_date]).order_by('-date')
    else:
        unsorted_spending = Spending.objects.filter(
            spending_owner=request.user).order_by('-date')

    # retrieve spending by filtered type
    if selected_sort == 'Income':
        spending = unsorted_spending.filter(spending_type=Spending_type.INCOME)
    elif selected_sort == 'Expenditure':
        spending = unsorted_spending.filter(spending_type=Spending_type.EXPENDITURE)
    elif selected_sort:
        spending = unsorted_spending.order_by(selected_sort)
    else:
        spending = unsorted_spending.order_by('date')

    paginator = Paginator(spending, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    add_form = AddSpendingForm(user=request.user)
    edit_form = EditSpendingForm(user=request.user)
    context = {'add_form': add_form, 'edit_form': edit_form, 'spending': spending, 'page_obj': page_obj}

    # if the request was sent by Ajax, render spending table html
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
            # create new SpendingFile object associated with the spending object and replace the old SpendingFile
            if file_list:
                SpendingFile.objects.filter(spending=spending).delete()
                for file in file_list:
                    SpendingFile.objects.create(
                        spending=spending,
                        file=file
                    )
            # delete file(s) the user upload if delete_file field is selected                    
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
            # create SpendingFile object to contain the file(s) the user
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

# This view function allow user to add a new spending category to their list of categories
@login_required
def add_spending_categories(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            if Categories.objects.filter(owner=request.user).count() < 30:
                category = form.save(commit=False)
                category.owner = request.user
                category.save()
                messages.add_message(request, messages.SUCCESS, "Category successfully added")
            else:
                messages.add_message(request, messages.ERROR, "You can only have a maximum of 30 categories")
            return redirect('view_spending_categories')
    else:
        form = CategoriesForm()
    return render(request, 'view_spending_categories.html', {'form': form})

# This function is a helper function user when add spending. It auto change the content of the dropdown menu for categories automatically when the content in spending_type change
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


# This function is for viewing all the categories belongs to current user
# The list of categories are passing into the html base on their spending_type
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

# This function is for deleting an existing category
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

# This function is for updating an existing category
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
    guide_list = [
    "1. We have a lot of exciting features waiting for you to discover in the Settings page. So why not take a look and explore all the possibilities?",
    "2. If you want to get the daily point, simply click on the piggy image on the overview page.",
    "3. Tracking your spending is easy! Just head over to the overview page and click on \"Bookkeeping\". Then, fill in the Title, amount, description, date, "
    "Spending type, and Spending category for each spending you make and hit \"Add\".",
    "4. If you want to see your history activities, just Go to the \"Report\" page to view a summary of your Expenditure and Income.",
    "5. To set your budget limit, go to the \"My Plan\" page and click on \"Set Total Budget\". Then, simply enter the amount you want to spend, "
    "choose how long you want the budget to last, and save your changes. After that, click on set specific budget Button to set your category budget.",
    "6. Don't worry about having to manually refresh your budget, it'll automatically be reset to the same limit once the time period you chose is up.",
    "7. If you really want to reset your budget manually, you can go to settings page and change your total budget limit in the \"Reset Total Budget\" section",
    "8. Want to add a profile picture to your account? You can easily do so by visiting https://en.gravatar.com/ and following the instructions there.",
    "9. If you'd like to share your daily accounting routine and inspire others, why not try using our forum feature? "
    "It's a great way to connect with other users and exchange helpful tips and advice!",
    "10. Need help navigating our app? Try using some keywords like \"hello\", \"budget\", \"expense\", \"track\", \"saving\", \"finance\", \"bye\", "
    "or anything else you have questions about, to chat with our helpful chatbot.",
    "11. Ready to cash in your daily points for some awesome rewards? Simply click on the 'Reward' button and choose from our selection of great prizes. It's that easy!",
    "12. The calendar at the home page shows your spendings of each day in the current month, you can also click on the link on top of the calendar to get access to all "
    "the months' spending calendars.",
    "13. The \"Monthly Revenue\" and \"Monthly Expense\" sections in the home page shows your total amount of income and expenditure of the current month respectively. "
    "And the \"My Plan\" section shows the total budget you set."
    "14. If you wish to edit your personal information, then you can submit your information through \"My Profile\" section",
    "15. Remember you can always reset your password by clicking on the \"Edit Password\" option from the drop down list under your user icon image!"
    ]
    sorted_guide_list = sorted(guide_list, key=lambda x: float(x.split()[0].replace('.', '')))

    # Add a paginator so a single page only shows at most 5 user guide lines
    paginator = Paginator(sorted_guide_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user_guideline.html', {'page_obj': page_obj})


@login_required
def spending_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_categories = request.GET.get('selected_categories')
    sorted = request.GET.get('sorted')
    # Filter spendings data by timeframe
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        spendings = Spending.objects.filter(spending_owner=request.user, date__range=[start_date, end_date])
    else:
        spendings = Spending.objects.filter(spending_owner=request.user)

    # Filter spendings data by spending type
    if selected_categories == 'Income':
        report_type = 'Income'
        selected_spendings = spendings.filter(spending_type=Spending_type.INCOME)
    else:
        report_type = 'Expenditure'
        selected_spendings = spendings.filter(spending_type=Spending_type.EXPENDITURE)
    spendings_data = selected_spendings.values('spending_category__name').annotate(exp_amount=Sum('amount'))

    # Sort spendings data by spending category, amount, or date
    if sorted == 'spending_category':
        sorted_spendings = selected_spendings.order_by('spending_category')
    elif sorted == 'amount':
        sorted_spendings = selected_spendings.order_by('amount')
    elif sorted == '-amount':
        sorted_spendings = selected_spendings.order_by('-amount')
    elif sorted == 'date':
        sorted_spendings = selected_spendings.order_by('date')
    else:
        sorted_spendings = selected_spendings.order_by('-date')

    # Add paginator so every page contains only 10 rows of spending data
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
    sorted_category_budgets = sort_category_budget(request, selected_sort, category_budgets)
    form = TotalBudgetForm(request.user)
    specific_form = BudgetForm(request.user)

    return render(request, 'budget_show.html', {
        'budget': total_budget,
        'spending_percentage': percentage,
        'category_budgets': sorted_category_budgets,
        'form': form,
        'specific_form': specific_form,
    })


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

# This function retrieves all posts from the database and orders them by their creation date, from newest to oldest, and attach with one reply
@login_required
def forum(request):
    posts = Post.objects.all().order_by('-created_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for post in page_obj:
        post.replies = Reply.objects.filter(parent_post=post)

    return render(request, 'forum.html', {'page_obj': page_obj})

# This view function displays a list of forum posts created by the current logged-in user
@login_required
def personal_forum(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for post in page_obj:
        post.replies = Reply.objects.filter(parent_post=post)

    return render(request, 'personal_forum.html', {'page_obj': page_obj})

# This function displays a page that shows all the replies made by the user in the forum
@login_required
def personal_forum_reply(request):
    reply_page_number = request.GET.get('reply_page')
    replies = Reply.objects.filter(user=request.user).order_by('-created_date')
    reply_paginator = Paginator(replies, 5)
    reply_page_obj = reply_paginator.get_page(reply_page_number)

    return render(request, 'personal_forum_reply.html', {'reply_page_obj': reply_page_obj})

# This view function allows users to add a new post to the forum
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
            messages.add_message(request, messages.SUCCESS,
                                 "post has been successfully added!")
            return redirect('forum')
    else:
        form = PostForm()
    return render(request, 'add_post.html',  {'form': form})

# This function allows users to delete their own posts
@login_required
def delete_post(request, post_id):
    delete_post = get_object_or_404(Post, id=post_id)
    delete_post.delete()
    messages.warning(request, "post has been deleted")
    return redirect('personal_forum')

# This function retrieves details of a specific post and its replies based on the post_id parameter
@login_required
def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponseNotFound()
    replies = Reply.objects.filter(parent_post=post).order_by('created_date')
    paginator = Paginator(replies, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'post': post, 'replies': replies, 'page_obj': page_obj}
    return render(request, 'post_detail.html', context)

# This function allows users to like or unlike a post or reply
@login_required
def like(request, post_reply_id, post_id=None):
    obj = None
    content_type = None
    if post_id:
        obj = get_object_or_404(Reply, id=post_reply_id)
        content_type = ContentType.objects.get_for_model(Reply)
    else:
        obj = get_object_or_404(Post, id=post_reply_id)
        content_type = ContentType.objects.get_for_model(Post)
    user = request.user
    try:
        like = Like.objects.get(
            content_type=content_type,
            object_id=post_reply_id,
            user=user,
        )
        like.delete()
        created = False
    except Like.DoesNotExist:
        like = Like.objects.create(
            content_type=content_type,
            object_id=post_reply_id,
            user=user,
        )
        created = True
    redirect_url = request.META.get(
        'HTTP_REFERER', reverse('post_detail', args=[post_id])) if post_id else request.META.get('HTTP_REFERER', reverse('forum'))
    return redirect(redirect_url)

# This function allows users to reply a post or a reply
@login_required
def add_reply(request, post_id, parent_reply_id=None):
    post = get_object_or_404(Post, id=post_id)
    parent_reply = get_object_or_404(Reply, id=parent_reply_id) if parent_reply_id else None

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.parent_post = post
            reply.parent_reply = parent_reply
            reply.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Reply has been successfully added!")
            return redirect('post_detail', post_id=post.id)
    else:
        form = ReplyForm()

    context = {'form': form, 'post': post, 'parent_reply': parent_reply}
    template_name = 'add_reply_to_reply.html' if parent_reply else 'add_reply_to_post.html'
    return render(request, template_name, context)

# This view function deletes a reply and redirects the user to their personal forum reply page
@login_required
def delete_reply(request, reply_id):
    delete_reply = get_object_or_404(Reply, id=reply_id)
    delete_reply.delete()
    messages.warning(request, "reply has been deleted")
    return redirect('personal_forum_reply')

# This function displays the details of a post created by a particular user
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


# This method allows a logged-in user to set a specific budget for a spending category.
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


# This method allows a user to change their password if they are already authenticated.
# It checks if the current password entered is correct and validates the new password according to certain criteria.
# If everything is valid, it updates the password and logs in the user with the new password.
# Finally, a template with a password form will be rendered.
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


# This function creates a new budget for the user if their current budget has ended.
# It checks if the user has a current budget and if the end date of the budget has passed.
# If so, it creates a new budget for the user with the same limit, a start date of today's date,
# an end date of 30 days from today's date, and assigns the budget to the user.
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


# This function gets all expenditure categories belonging to the current user and returns a list of dictionaries
# containing the category name, budget limit, spending amount, and percentage of spending (if applicable).
# It calculates the spending amount by querying the Spending model for expenses
# within the current total budget period and sums up the amounts for each category.
# If the category has no budget set, the budget value is set to "Not set yet",
# and the spending percentage is set to None.
# If there is no total budget set, the spending value is set to "Please set a total budget first".
@login_required
def get_category_budgets(request, total_budget):
    categories = Categories.objects.filter(owner=request.user, categories_type=Spending_type.EXPENDITURE)
    category_budgets = []
    for category in categories:
        budget = Budget.objects.filter(spending_category=category).last()
        if budget:
            result = Spending.objects.filter(
                spending_owner=request.user,
                date__range=(total_budget.start_date, total_budget.end_date),
                spending_type=Spending_type.EXPENDITURE,
                spending_category=category,
            ).aggregate(nums=Sum('amount')).get('nums') or 0

            spending_sum = round(result, 2)
            category_budgets.append({
                'name': category.name,
                'budget': budget.limit,
                'spending': spending_sum,
                'percentage': int(spending_sum / budget.limit * 100) if budget.limit else None,
            })
        else:
            if total_budget:
                result = Spending.objects.filter(spending_owner=request.user,
                                                       date__range=(total_budget.start_date, total_budget.end_date),
                                                       spending_type=Spending_type.EXPENDITURE,
                                                       spending_category=category,
                                                       ).aggregate(nums=Sum('amount')).get('nums') or 0

                spending_sum = round(result, 2)
                
                category_budgets.append({
                    'name': category.name,
                    'budget': 'Not set yet',
                    'spending': spending_sum,
                    'percentage': None,
                })
            else:
                category_budgets.append(
                    {'name': category.name, 'budget': 'Not set yet', 'spending': 'Please set a total budget first',
                     'percentage': None,
                     })
    return category_budgets


# This function sorts the list of dictionaries based on the selected sorting option and returns the sorted list.
@login_required
def sort_category_budget(request, selected_sort, category_budgets):
    if selected_sort == '-budget':
        sorted_category_budgets = sorted(
            category_budgets,
            key=lambda k: (k['budget'] != 'Not set yet',
                float(k['budget']) if isinstance(k['budget'], str) and k['budget'] != 'Not set yet' else k['budget']
            ),
            reverse=True
        )
    elif selected_sort == 'budget':
        sorted_category_budgets = sorted(
            category_budgets,
            key=lambda k: (k['budget'] != 'Not set yet',
                float(k['budget']) if isinstance(k['budget'], str) and k['budget'] != 'Not set yet' else k['budget']
            )
        )
    elif selected_sort == '-spending':
        sorted_category_budgets = sorted(
            category_budgets,
            key=lambda k: (k['spending'] != 'Please set a total budget first',
                float(k['spending']) if isinstance(k['spending'], str) and k['spending'] != 'Please set a total budget first' else k['spending']
            ),
            reverse=True
        )
    elif selected_sort == 'spending':
        sorted_category_budgets = sorted(category_budgets, key=lambda k: (k['spending'] != 'Please set a total budget first',
        float(k['spending']) if isinstance(k['spending'], str) and k['spending'] != 'Please set a total budget first' else k['spending']
            ),
        )
    elif selected_sort == '':
        sorted_category_budgets = category_budgets
    else:
        sorted_category_budgets = category_budgets
    return sorted_category_budgets