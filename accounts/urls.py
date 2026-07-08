from django.urls import path
from . import views

urlpatterns = [

    # Home
    path("", views.home, name="home"),

    # Authentication
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Staff Approval
    path(
        "staff-approval/",
        views.staff_approval,
        name="staff_approval"
    ),

    path(
        "staff-approval/<int:profile_id>/approve/",
        views.approve_staff,
        name="approve_staff"
    ),

    path(
        "staff-approval/<int:profile_id>/reject/",
        views.reject_staff,
        name="reject_staff"
    ),

    path(
        "staff/",
        views.staff_list,
        name="staff_list"
    ),

    path(
        "staff/<int:pk>/",
        views.staff_detail,
        name="staff_detail"
    ),

    path(
        "staff/<int:pk>/edit/",
        views.staff_edit,
        name="staff_edit"
    ),

    path(
        "staff/<int:pk>/delete/",
        views.staff_delete,
        name="staff_delete"
    ),

]