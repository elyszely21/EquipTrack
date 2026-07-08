from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Equipment
from .forms import EquipmentForm


@login_required
def dashboard(request):
    return render(request, "dashboard/index.html")

@login_required
def equipment_list(request):

    equipments = Equipment.objects.all()

    context = {
        "equipments": equipments,
        "profile": request.user.profile,
    }

    return render(
        request,
        "equipment/equipment_list.html",
        context,
    )

@login_required
def equipment_create(request):

    if request.method == "POST":

        form = EquipmentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Equipment added successfully."
            )

            return redirect("equipment_list")

    else:

        form = EquipmentForm()

    return render(
        request,
        "equipment/equipment_form.html",
        {
            "form": form,
            "title": "Add Equipment",
            "profile": request.user.profile,
        }
    )

@login_required
def equipment_update(request, equipment_id):

    equipment = get_object_or_404(
        Equipment,
        equipment_id=equipment_id
    )

    if request.method == "POST":

        form = EquipmentForm(
            request.POST,
            instance=equipment
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Equipment updated successfully."
            )

            return redirect("equipment_list")

    else:

        form = EquipmentForm(
            instance=equipment
        )

    return render(
        request,
        "equipment/equipment_form.html",
        {
            "form": form,
            "title": "Edit Equipment",
            "profile": request.user.profile,
        }
    )

@login_required
def equipment_detail(request, equipment_id):

    equipment = get_object_or_404(
        Equipment,
        equipment_id=equipment_id
    )

    return render(
        request,
        "equipment/equipment_detail.html",
        {
            "equipment": equipment,
            "profile": request.user.profile,
        }
    )

@login_required
def equipment_delete(request, equipment_id):

    equipment = get_object_or_404(
        Equipment,
        equipment_id=equipment_id
    )

    if request.method == "POST":

        equipment.delete()

        messages.success(
            request,
            "Equipment deleted successfully."
        )

        return redirect("equipment_list")

    return render(
        request,
        "equipment/equipment_delete.html",
        {
            "equipment": equipment,
            "profile": request.user.profile,
        }
    )
