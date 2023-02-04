from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import render,redirect
from django.contrib import messages
from pst.forms import VisitorSignupForm
from pst.helpers.auth import login_prohibited
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

def visitor_introduction(request):
    return render(request, 'visitor_introduction.html')

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
        "psc": ["Our Personal Spending Tracker helps you keep track of your daily expenses and budget. Is there anything specific you would like to know?", 
                "Our PSC is designed to help manage your personal finances, including tracking expenses and setting budgets. How can I assist you?"],
        "budget": ["You can use our Personal Spending Tracker to set budgets for different categories of expenses. Let me know if you need help with that!", 
                    "Our PSC allows you to set a monthly or weekly budget to keep your spending in check. Would you like a demo on how to set a budget?"],
        "expense": ["You can log all your expenses on our Personal Spending Tracker, including the date, category, and amount spent. Would you like help tracking an expense?", 
                    "With the Personal Spending Tracker, you can easily keep track of all your expenses, both big and small. Let me know if you need assistance logging an expense."],
        "track": ["Our Personal Spending Tracker is designed to help you keep track of your daily expenses, budget, and savings. Let me know if you need help tracking something!", 
                    "The PSC is a powerful tool for tracking your spending, budget, and savings. How can I assist you with tracking?"],
        "saving": ["Our Personal Spending Tracker can help you track your savings and keep you on track to reach your financial goals. Let me know if you need help setting up a savings plan!", 
                    "The PSC is a great tool for tracking your savings and sticking to your budget. Would you like help setting up a savings plan?"],
        "finance": ["Our Personal Spending Tracker is a comprehensive tool for managing your personal finances. It includes features for tracking expenses, setting budgets, and monitoring savings. Let me know if you need help with anything!", 
                    "With the PSC, you can take control of your personal finances and make informed decisions about your spending and saving. Would you like a demo on how to use it?"],
        "hello": ["Hello! How may I help you?", "Hi there! How can I assist you today with our Personal Spending Tracker?"],
        "bye": ["Goodbye! Have a great day!", "See you later! Take care and don't hesitate to reach out if you need help with the Personal Spending Tracker."],
    }

    tokens = word_tokenize(user_input)
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]

    for keyword, synonyms in keywords.items():
        for token in tokens:
            if token in synonyms:
                return random.choice(responses[keyword])
    return "Sorry, I do not understand what you mean."




