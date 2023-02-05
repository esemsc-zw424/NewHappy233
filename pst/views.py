from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import render,redirect
from django.contrib import messages
from pst.forms import VisitorSignupForm, LoginForm
from pst.helpers.auth import login_prohibited
from django.contrib.auth import authenticate, login, logout

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
        "psc": ["personal spending tracker", "psc"],
        "budget": ["budget", "spending budget", "financial budget"],
        "expense": ["expense", "spending", "financial expense"],
        "track": ["track", "record", "keep track"],
        "saving": ["saving", "save", "financial saving"],
        "finance": ["finance", "financial management", "money management"],
        "hello": ["hi", "hello", "hey", "greetings", "heya", "hola", "what's up", "sup"],
        "bye": ["bye", "goodbye", "see you later", "adios", "later", "farewell"]
    }

    responses = {
        "psc": ["Our Personal Spending Tracker helps you keep track of your daily expenses and budget."], 
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




