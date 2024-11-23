from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from .utils import *


# @login_required(login_url="login")
def LandingPage(request):
    return render(request, 'park/landing.html')


def About(request):
    return render(request, 'park/about.html')

def Services(request):
    return render(request, 'park/reviews.html')

def Reviews(request):
    return render(request, 'park/services.html')

def Login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.info(request, "Username or Password is Incorrect")
    return render(request, 'park/login.html')

def Register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
            
                system_messages = messages.get_messages(request)
                for message in system_messages:
                    # This iteration is necessary
                    pass


                messages.success(request, "Account Created For " + user)
                return redirect('login')
            else:
                system_messages = messages.get_messages(request)
                for message in system_messages:
                    # This iteration is necessary
                    pass
                messages.info(request, "Make Sure your Credentials is Correct or Valid")
            
    context = {"form": form}
    return render(request, 'park/login.html', context)

def Logout(request):
    logout(request)
    return redirect('login')

def Dashboard(request):
    return render(request, 'park/dashboard.html')