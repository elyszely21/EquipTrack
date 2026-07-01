"""
URL configuration for EquipTrack.
"""
from django.urls import include, path


urlpatterns = [
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
]
