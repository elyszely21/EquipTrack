from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("staff-approval/", views.staff_approval, name="staff_approval"),
    path("staff-approval/<int:profile_id>/approve/", views.approve_staff, name="approve_staff"),
    path("staff-approval/<int:profile_id>/reject/", views.reject_staff, name="reject_staff"),
]
