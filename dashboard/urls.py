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

    # ==========================
    # Borrow Requests
    # ==========================

    path(
        "borrow/",
        views.borrow_list,
        name="borrow_list",
    ),

    path(
        "borrow/new/",
        views.borrow_create,
        name="borrow_create",
    ),

    path(
        "borrow/<int:request_id>/",
        views.borrow_detail,
        name="borrow_detail",
    ),

    path(
        "borrow/<int:request_id>/delete/",
        views.borrow_delete,
        name="borrow_delete",
    ),

    path(
        "borrow/<int:request_id>/approve/",
        views.approve_borrow,
        name="approve_borrow",
    ),

    path(
        "borrow/<int:request_id>/reject/",
        views.reject_borrow,
        name="reject_borrow",
    ),

    # ==========================
    # Returns
    # ==========================

    path(
        "returns/",
        views.return_list,
        name="return_list",
    ),

    path(
        "returns/<int:request_id>/process/",
        views.create_return,
        name="create_return",
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
    # Reports
    # ==========================

    path(
        "reports/",
        views.reports,
        name="reports",
    ),

    path(
        "reports/export/excel/",
        views.reports_export_excel,
        name="reports_export_excel",
    ),

    path(
        "reports/export/pdf/",
        views.reports_export_pdf,
        name="reports_export_pdf",
    ),

    # ==========================
    # Users
    # ==========================

    path(
        "users/",
        views.user_list,
        name="user_list",
    ),

    # ==========================
    # Profile
    # ==========================

    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),

    path(
        "profile/change-password/",
        views.change_password,
        name="change_password",
    ),
]
