from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    context = {
        "total_equipment": 0,
        "available_equipment": 0,
        "borrowed_equipment": 0,
        "returned_equipment": 0,
    }
    return render(request, "dashboard/index.html", context)
