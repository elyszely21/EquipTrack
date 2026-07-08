from django.urls import path
from . import views

urlpatterns = [

    path("", views.dashboard, name="dashboard"),

    # ==========================
    # Equipment
    # ==========================

    path(
        "equipment/",
        views.equipment_list,
        name="equipment_list",
    ),

    path(
        "equipment/add/",
        views.equipment_create,
        name="equipment_create",
    ),

    path(
        "equipment/<int:equipment_id>/",
        views.equipment_detail,
        name="equipment_detail",
    ),

    path(
        "equipment/<int:equipment_id>/edit/",
        views.equipment_update,
        name="equipment_update",
    ),

    path(
        "equipment/<int:equipment_id>/delete/",
        views.equipment_delete,
        name="equipment_delete",
    ),
]