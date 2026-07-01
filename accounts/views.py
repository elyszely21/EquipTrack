from django.shortcuts import render

def login_view(request):
    return render(request, 'registration/login.html')


def register_view(request):
    return render(request, 'registration/register.html')