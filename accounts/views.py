from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .forms import (
    UserRegistrationForm,
    LoginForm,
    ProfileForm,
    PasswordChangeForm,
    StaffForm,
)
from .models import UserProfile, Staff
from .utils import is_admin_user
from . import services


def home(request):
    return redirect("login")


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = services.register_user(form.cleaned_data)

            if user.profile.role == UserProfile.ROLE_STAFF:
                messages.success(
                    request,
                    "Registration submitted successfully. Your account is awaiting administrator approval.",
                )
            else:
                messages.success(
                    request,
                    "Registration successful. You may now log in.",
                )
            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user, profile = services.authenticate_user(username, password)

            if user is not None:
                if profile.status == UserProfile.STATUS_PENDING:
                    messages.warning(
                        request,
                        "Your account is awaiting administrator approval.",
                    )
                    return redirect("login")

                if profile.status == UserProfile.STATUS_REJECTED:
                    messages.error(
                        request,
                        "Your registration has been rejected. Please contact the administrator.",
                    )
                    return redirect("login")

                login(request, user)

                if not form.cleaned_data.get("remember_me"):
                    request.session.set_expiry(0)

                return redirect("dashboard")

            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ============================================================================
# STAFF APPROVAL VIEWS
# ============================================================================


@login_required
def staff_approval(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden("Only administrators can approve staff registrations.")

    staff_profiles = services.get_pending_staff_profiles()

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

    profile = services.approve_staff_registration(profile_id)
    if profile is None:
        messages.error(request, "Staff registration was not found or is no longer pending.")
    else:
        messages.success(request, "Staff registration approved successfully.")

    return redirect("staff_approval")


@login_required
def reject_staff(request, profile_id):
    if request.method != "POST":
        return redirect("staff_approval")

    if not is_admin_user(request.user):
        return HttpResponseForbidden("Only administrators can reject staff registrations.")

    profile = services.reject_staff_registration(profile_id)
    if profile is None:
        messages.error(request, "Staff registration was not found or is no longer pending.")
    else:
        messages.success(request, "Staff registration rejected successfully.")

    return redirect("staff_approval")


# ============================================================================
# STAFF MANAGEMENT VIEWS
# ============================================================================


@login_required
def staff_list(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    search = request.GET.get("search", "").strip()
    staff = services.get_staff_list(search)

    return render(
        request,
        "staff/staff_list.html",
        {
            "staff": staff,
            "search": search,
            "profile": request.user.profile,
        },
    )


@login_required
def staff_detail(request, pk):
    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    staff = services.get_staff_detail(pk)
    if staff is None:
        from django.http import Http404
        raise Http404

    return render(
        request,
        "staff/staff_detail.html",
        {
            "staff": staff,
            "profile": request.user.profile,
        },
    )


@login_required
def staff_edit(request, pk):
    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    staff = get_object_or_404(
        Staff.objects.select_related("user_profile", "user_profile__user"),
        pk=pk,
    )

    if request.method == "POST":
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff updated successfully.")
            return redirect("staff_list")
    else:
        form = StaffForm(instance=staff)

    return render(
        request,
        "staff/staff_form.html",
        {
            "form": form,
            "staff": staff,
            "profile": request.user.profile,
        },
    )


@login_required
def staff_delete(request, pk):
    if not is_admin_user(request.user):
        return HttpResponseForbidden()

    staff = get_object_or_404(
        Staff.objects.select_related("user_profile", "user_profile__user"),
        pk=pk,
    )

    if request.method == "POST":
        staff.delete()
        messages.success(request, "Staff deleted successfully.")
        return redirect("staff_list")

    return render(
        request,
        "staff/staff_delete.html",
        {
            "staff": staff,
            "profile": request.user.profile,
        },
    )


# ============================================================================
# PROFILE VIEWS
# ============================================================================


@login_required
def profile_view(request):
    return render(
        request,
        "profile/profile.html",
        {"profile": request.user.profile},
    )


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            instance=profile,
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            },
        )

        if form.is_valid():
            services.update_user_profile(request.user, form.cleaned_data)
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(
            instance=profile,
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            },
        )

    return render(
        request,
        "profile/edit_profile.html",
        {
            "form": form,
            "profile": request.user.profile,
        },
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "profile/change_password.html",
        {"form": form},
    )
