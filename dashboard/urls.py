from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # Dashboard
    # ==========================

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

    # ==========================
    # Inventory
    # ==========================

    path(
        "inventory/",
        views.inventory_list,
        name="inventory_list",
    ),

    path(
        "inventory/low-stock/",
        views.low_stock,
        name="low_stock",
    ),

    # ==========================
    # Borrow Requests
    # ==========================

    path(
        "borrow/",
        views.borrow_list,
        name="borrow_list",
    ),

    path(
        "borrow/add/",
        views.borrow_create,
        name="borrow_create",
    ),

    path(
        "borrow/<int:request_id>/",
        views.borrow_detail,
        name="borrow_detail",
    ),

    path(
        "borrow/<int:request_id>/update/",
        views.borrow_update,
        name="borrow_update",
    ),

    path(
        "borrow/<int:request_id>/delete/",
        views.borrow_delete,
        name="borrow_delete",
    ),

    # ==========================
    # Return Records
    # ==========================

    path(
        "return/",
        views.return_list,
        name="return_list",
    ),

    path(
        "return/add/<int:request_id>/",
        views.return_create,
        name="create_return",
    ),

    path(
        "return/<int:transaction_id>/",
        views.return_detail,
        name="return_detail",
    ),

    # ==========================
    # Reports
    # ==========================

    path(
        "reports/",
        views.reports,
        name="reports",
    ),
]