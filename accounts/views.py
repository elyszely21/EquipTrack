from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import UserRegistrationForm, LoginForm
from .models import UserProfile

def home(request):
    return redirect("login")

def register(request):

    if request.method == "POST":

        form = UserRegistrationForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(

                username=form.cleaned_data["username"],

                first_name=form.cleaned_data["first_name"],

                last_name=form.cleaned_data["last_name"],

                email=form.cleaned_data["email"],

                password=form.cleaned_data["password"]

            )

            profile = user.profile
            profile.middle_name = form.cleaned_data["middle_name"]
            profile.suffix = form.cleaned_data["suffix"]
            profile.contact_number = form.cleaned_data["contact_number"]
            profile.role = form.cleaned_data["role"]
            profile.save()

            messages.success(
                request,
                "Account created successfully."
            )

            return redirect("login")

    else:

        form = UserRegistrationForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form
        }
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]

            password = form.cleaned_data["password"]

            user = authenticate(

                username=username,

                password=password

            )

            if user is not None:

                login(request, user)

                return redirect("dashboard")

            messages.error(
                request,
                "Invalid username or password."
            )

    else:

        form = LoginForm()

    return render(
        request,
        "registration/login.html",
        {
            "form": form
        }
    )

@login_required
def dashboard(request):

    profile = request.user.profile

    context = {

        "user": request.user,

        "profile": profile

    }

    return render(

        request,

        "dashboard/index.html",

        context

    )

@login_required
def logout_view(request):

    logout(request)

    return redirect("login")
