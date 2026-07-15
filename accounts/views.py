from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from .forms import UserRegistrationForm, LoginForm, StaffForm
from .models import UserProfile, Staff

def home(request):
    return redirect("login")


def is_admin_user(user):
    return (
        user.is_authenticated
        and hasattr(user, "profile")
        and user.profile.role == UserProfile.ROLE_ADMIN
        and user.profile.status == UserProfile.STATUS_ACTIVE
    )

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
            profile.department = form.cleaned_data["department"]
            profile.position = form.cleaned_data["position"]
            profile.role = form.cleaned_data["role"]
            profile.status = (
                UserProfile.STATUS_PENDING
                if profile.role == UserProfile.ROLE_STAFF
                else UserProfile.STATUS_ACTIVE
            )
            profile.save()

            if profile.role == UserProfile.ROLE_STAFF:
                messages.success(
                    request,
                    "Registration submitted successfully. Your account is awaiting administrator approval."
                )
            else:
                messages.success(
                    request,
                    "Registration successful. You may now log in."
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

            user = authenticate(username=username, password=password)

            if user is not None:
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "contact_number": "",
                        "role": UserProfile.ROLE_ADMIN if user.is_superuser else UserProfile.ROLE_BORROWER,
                        "status": UserProfile.STATUS_ACTIVE,
                    },
                )

                if profile.status == UserProfile.STATUS_PENDING:
                    messages.warning(
                        request,
                        "Your account is awaiting administrator approval."
                    )
                    return redirect("login")

                if profile.status == UserProfile.STATUS_REJECTED:
                    messages.error(
                        request,
                        "Your registration has been rejected. Please contact the administrator."
                    )
                    return redirect("login")

                login(request, user)

                if not form.cleaned_data.get("remember_me"):
                    request.session.set_expiry(0)

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
def logout_view(request):

    logout(request)

    return redirect("login")


@login_required
def staff_approval(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden("Only administrators can approve staff registrations.")

    staff_profiles = (
        UserProfile.objects
        .select_related("user")
        .filter(role=UserProfile.ROLE_STAFF)
        .order_by("status", "user__date_joined")
    )

    return render(
        request,
        "accounts/staff_approval.html",
        {
            "staff_profiles": staff_profiles,
            "profile": request.user.profile,
        },
    )


@login_required
def approve_staff(request, profile_id):
    if request.method != "POST":
        return redirect("staff_approval")

    if not is_admin_user(request.user):
        return HttpResponseForbidden("Only administrators can approve staff registrations.")

    profile = UserProfile.objects.filter(
        id=profile_id,
        role=UserProfile.ROLE_STAFF,
        status=UserProfile.STATUS_PENDING,
    ).first()

    if profile is None:
        messages.error(request, "Staff registration was not found or is no longer pending.")
        return redirect("staff_approval")

    profile.status = UserProfile.STATUS_ACTIVE
    profile.save(update_fields=["status"])

    Staff.objects.get_or_create(
        user_profile=profile,
        defaults={
            "department": profile.department or "Unassigned",
        },
    )

    messages.success(request, "Staff registration approved successfully.")

    return redirect("staff_approval")


@login_required
def reject_staff(request, profile_id):
    if request.method != "POST":
        return redirect("staff_approval")

    if not is_admin_user(request.user):
        return HttpResponseForbidden("Only administrators can reject staff registrations.")

    profile = UserProfile.objects.filter(
        id=profile_id,
        role=UserProfile.ROLE_STAFF,
        status=UserProfile.STATUS_PENDING,
    ).first()

    if profile is None:
        messages.error(request, "Staff registration was not found or is no longer pending.")
        return redirect("staff_approval")

    profile.status = UserProfile.STATUS_REJECTED
    profile.save(update_fields=["status"])
    messages.success(request, "Staff registration rejected successfully.")

    return redirect("staff_approval")

@login_required
def staff_list(request):

    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    search = request.GET.get("search", "").strip()

    staff = Staff.objects.select_related("user_profile__user").all()

    if search:
        staff = staff.filter(
            Q(user_profile__user__first_name__icontains=search) |
            Q(user_profile__user__last_name__icontains=search) |
            Q(user_profile__user__username__icontains=search) |
            Q(department__icontains=search)
        )

    paginator = Paginator(staff, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "staff": page_obj,
        "page_obj": page_obj,
        "search": search,
        "profile": request.user.profile,
    }

    return render(
        request,
        "staff/staff_list.html",
        context,
    )


@login_required
def staff_detail(request, pk):

    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    staff = get_object_or_404(Staff, pk=pk)

    return render(
        request,
        "staff/staff_detail.html",
        {
            "staff": staff,
            "profile": request.user.profile,
        }
    )


@login_required
def staff_edit(request, pk):

    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    staff = get_object_or_404(
        Staff,
        pk=pk
    )

    if request.method == "POST":

        form = StaffForm(
            request.POST,
            instance=staff
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Staff updated successfully."
            )

            return redirect(
                "staff_list"
            )

    else:

        form = StaffForm(
            instance=staff
        )

    return render(
        request,
        "staff/staff_form.html",
        {
            "form": form,
            "staff": staff,
            "profile": request.user.profile,
        }
    )

@login_required
def staff_delete(request, pk):

    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    staff = get_object_or_404(
        Staff,
        pk=pk
    )

    if request.method == "POST":

        staff.delete()

        messages.success(
            request,
            "Staff deleted successfully."
        )

        return redirect(
            "staff_list"
        )

    return render(
        request,
        "staff/staff_delete.html",
        {
            "staff": staff,
            "profile": request.user.profile,
        }
    )
