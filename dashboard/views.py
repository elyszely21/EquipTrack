import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)

from .models import Equipment, BorrowRequest
from .forms import EquipmentForm
from . import services
from .utils import is_admin_user, is_staff_user, is_borrower_user, is_admin_or_staff, get_safe_profile


# ============================================================================
# DASHBOARD VIEW
# ============================================================================


@login_required
def dashboard(request):
    """Main dashboard with inventory and borrow statistics."""
    context = services.get_dashboard_context(request.user)
    context["profile"] = get_safe_profile(request.user)
    return render(request, "dashboard/index.html", context)


# ============================================================================
# EQUIPMENT VIEWS
# ============================================================================


@login_required
def equipment_list(request):
    """List all equipment with search, filters, and pagination."""
    search = request.GET.get("search", "")
    category_filter = request.GET.get("category_filter", "")
    status_filter = request.GET.get("status_filter", "")
    stock_filter = request.GET.get("stock_filter", "")
    order_by = request.GET.get("order_by", "name")
    page = request.GET.get("page")

    context = services.get_equipment_list_context(
        search, category_filter, status_filter, stock_filter, order_by, page,
    )
    context["profile"] = get_safe_profile(request.user)
    return render(request, "equipment/equipment_list.html", context)


@login_required
def equipment_create(request):
    """Create new equipment."""
    if not is_admin_or_staff(request.user):
        messages.error(request, "You do not have permission to create equipment.")
        return redirect("equipment_list")

    if request.method == "POST":
        form = EquipmentForm(request.POST)
        try:
            is_valid = form.is_valid()
        except Exception:
            logger.exception("Error validating equipment form")
            messages.error(request, "An error occurred while validating the form. Please try again.")
            return render(
                request,
                "equipment/equipment_form.html",
                {
                    "form": form,
                    "title": "Add Equipment",
                    "profile": get_safe_profile(request.user),
                },
            )
        if is_valid:
            try:
                equipment = form.save()
            except Exception:
                logger.exception("Failed to save equipment")
                messages.error(
                    request,
                    "An error occurred while saving. Please try again.",
                )
                return render(
                    request,
                    "equipment/equipment_form.html",
                    {
                        "form": form,
                        "title": "Add Equipment",
                        "profile": get_safe_profile(request.user),
                    },
                )
            messages.success(request, f"Equipment '{equipment.name}' added successfully.")
            return redirect("equipment_list")
        else:
            logger.warning("EquipmentForm validation failed: %s", form.errors.as_json())
            messages.error(request, "Please correct the errors below.")
    else:
        form = EquipmentForm()

    return render(
        request,
        "equipment/equipment_form.html",
        {
            "form": form,
            "title": "Add Equipment",
            "profile": get_safe_profile(request.user),
        },
    )


@login_required
def equipment_update(request, equipment_id):
    """Update existing equipment."""
    if not is_admin_or_staff(request.user):
        messages.error(request, "You do not have permission to edit equipment.")
        return redirect("equipment_list")

    equipment = get_object_or_404(Equipment, equipment_id=equipment_id)

    if request.method == "POST":
        form = EquipmentForm(request.POST, instance=equipment)
        try:
            is_valid = form.is_valid()
        except Exception:
            logger.exception("Error validating equipment form for %s", equipment_id)
            messages.error(request, "An error occurred while validating the form. Please try again.")
            return render(
                request,
                "equipment/equipment_form.html",
                {
                    "form": form,
                    "title": "Edit Equipment",
                    "profile": get_safe_profile(request.user),
                    "equipment": equipment,
                },
            )
        if is_valid:
            try:
                form.save()
            except Exception:
                logger.exception("Failed to save equipment %s", equipment_id)
                messages.error(
                    request,
                    "An error occurred while saving. Please try again.",
                )
                return render(
                    request,
                    "equipment/equipment_form.html",
                    {
                        "form": form,
                        "title": "Edit Equipment",
                        "profile": get_safe_profile(request.user),
                        "equipment": equipment,
                    },
                )
            messages.success(request, f"Equipment '{equipment.name}' updated successfully.")
            return redirect("equipment_list")
        else:
            logger.warning("EquipmentForm validation failed for %s: %s", equipment_id, form.errors.as_json())
            messages.error(request, "Please correct the errors below.")
    else:
        form = EquipmentForm(instance=equipment)

    return render(
        request,
        "equipment/equipment_form.html",
        {
            "form": form,
            "title": "Edit Equipment",
            "profile": get_safe_profile(request.user),
            "equipment": equipment,
        },
    )


@login_required
def equipment_detail(request, equipment_id):
    """View equipment details and borrow history."""
    context = services.get_equipment_detail(equipment_id)
    context["profile"] = get_safe_profile(request.user)
    return render(request, "equipment/equipment_detail.html", context)


@login_required
def equipment_delete(request, equipment_id):
    """Delete equipment."""
    if not is_admin_or_staff(request.user):
        messages.error(request, "You do not have permission to delete equipment.")
        return redirect("equipment_list")

    equipment = get_object_or_404(Equipment, equipment_id=equipment_id)

    if request.method == "POST":
        equipment_name = equipment.name
        equipment.delete()
        messages.success(request, f"Equipment '{equipment_name}' deleted successfully.")
        return redirect("equipment_list")

    return render(
        request,
        "equipment/equipment_delete.html",
        {
            "equipment": equipment,
            "profile": get_safe_profile(request.user),
        },
    )


# ============================================================================
# INVENTORY VIEWS
# ============================================================================


@login_required
def inventory_list(request):
    """Inventory list with stock status, search, filters, and pagination."""
    search = request.GET.get("search", "")
    category_filter = request.GET.get("category_filter", "")
    status_filter = request.GET.get("status_filter", "")
    stock_filter = request.GET.get("stock_filter", "")
    order_by = request.GET.get("order_by", "name")
    page = request.GET.get("page")

    context = services.get_inventory_list_context(
        search, category_filter, status_filter, stock_filter, order_by, page,
    )
    context["profile"] = get_safe_profile(request.user)
    return render(request, "inventory/inventory_list.html", context)


@login_required
def low_stock(request):
    """List equipment with low or out of stock."""
    low_stock_items, out_of_stock_items = services.get_low_stock_items()
    return render(
        request,
        "inventory/low_stock.html",
        {
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "profile": get_safe_profile(request.user),
        },
    )


# ============================================================================
# BORROW REQUEST VIEWS
# ============================================================================


@login_required
def borrow_list(request):
    """List all borrow requests with search, filters, and pagination."""
    try:
        search = request.GET.get("search", "")
        status_filter = request.GET.get("status", "")
        user_filter = request.GET.get("user", "")
        date_from = request.GET.get("date_from", "")
        date_to = request.GET.get("date_to", "")
        order_by = request.GET.get("order_by", "-request_date")
        page = request.GET.get("page")

        context = services.get_borrow_list_context(
            request.user, search, status_filter, user_filter,
            date_from, date_to, order_by, page,
        )
        context["profile"] = get_safe_profile(request.user)
        return render(request, "borrow/borrow_list.html", context)
    except Exception:
        logger.exception("borrow_list view FAILED (user=%s)", request.user.pk)
        raise


@login_required
def borrow_detail(request, request_id):
    """View borrow request details."""
    try:
        borrow_request = services.get_borrow_detail(request_id)
        profile = get_safe_profile(request.user)

        if not (is_admin_user(request.user) or is_staff_user(request.user) or borrow_request.user == request.user):
            return HttpResponseForbidden("You don't have permission to view this request.")

        return render(
            request,
            "borrow/borrow_detail.html",
            {
                "borrow_request": borrow_request,
                "profile": profile,
            },
        )
    except Exception:
        logger.exception("borrow_detail view FAILED (request_id=%s, user=%s)", request_id, request.user.pk)
        raise


@login_required
def borrow_create(request):
    """
    Create a new borrow request (status=Pending).

    Stock is NOT reduced here. Inventory is decreased only when an admin
    approves the request.
    """
    if not (is_borrower_user(request.user) or is_staff_user(request.user) or is_admin_user(request.user)):
        return HttpResponseForbidden("You do not have permission to create borrow requests.")

    if request.method == "POST":
        equipment_ids = request.POST.getlist("equipment_ids")
        quantities_map = {eq_id: request.POST.get(f"quantity_{eq_id}", "") for eq_id in equipment_ids}

        try:
            borrow_request = services.create_borrow_request(
                request.user, equipment_ids, quantities_map,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("borrow_create")
        except Exception:
            logger.exception("Failed to create borrow request")
            messages.error(request, "An unexpected error occurred. Please try again.")
            return redirect("borrow_create")

        messages.success(
            request,
            "Borrow request submitted successfully and is awaiting admin approval.",
        )
        return redirect("borrow_detail", request_id=borrow_request.request_id)

    try:
        available_equipment = services.get_available_equipment()
        return render(
            request,
            "borrow/borrow_form.html",
            {
                "available_equipment": available_equipment,
                "profile": get_safe_profile(request.user),
            },
        )
    except Exception:
        logger.exception("borrow_create GET FAILED (user=%s)", request.user.pk)
        raise


@login_required
def borrow_update(request, request_id):
    """
    Approve or reject a pending borrow request.

    Approve: admin only -- decreases stock atomically.
    Reject: admin only -- no stock change.
    """
    if request.method != "POST":
        return redirect("borrow_detail", request_id=request_id)

    if not (is_admin_user(request.user) or is_staff_user(request.user)):
        return HttpResponseForbidden("Only administrators and staff can approve or reject borrow requests.")

    action = request.POST.get("action")
    if action not in ("approve", "reject"):
        messages.error(request, "Invalid action.")
        return redirect("borrow_detail", request_id=request_id)

    try:
        services.process_borrow_request(request_id, action, request.user)
    except BorrowRequest.DoesNotExist:
        messages.error(request, "Borrow request not found.")
        return redirect("borrow_list")
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("borrow_detail", request_id=request_id)
    except Exception:
        logger.exception("Failed to process borrow request %s", request_id)
        messages.error(request, "An unexpected error occurred while processing the request.")
        return redirect("borrow_detail", request_id=request_id)

    if action == "approve":
        messages.success(request, "Borrow request approved. Stock updated.")
    else:
        messages.success(request, "Borrow request rejected.")

    return redirect("borrow_detail", request_id=request_id)


@login_required
def borrow_delete(request, request_id):
    """
    Delete a pending borrow request.

    Borrowers may delete only their own pending requests.
    Admins may delete any pending request.
    """
    borrow_request = get_object_or_404(BorrowRequest, request_id=request_id)

    is_owner = borrow_request.user_id == request.user.id
    if not (is_admin_user(request.user) or is_staff_user(request.user) or is_owner):
        return HttpResponseForbidden("You don't have permission to delete this request.")

    if borrow_request.status != BorrowRequest.STATUS_PENDING:
        messages.error(request, "Only pending requests can be deleted.")
        return redirect("borrow_detail", request_id=borrow_request.request_id)

    if request.method == "POST":
        try:
            request_id_display = services.delete_borrow_request(request_id)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("borrow_detail", request_id=borrow_request.request_id)

        messages.success(request, f"Borrow request #{request_id_display} deleted successfully.")
        return redirect("borrow_list")

    return render(
        request,
        "borrow/borrow_delete.html",
        {
            "borrow_request": borrow_request,
            "profile": get_safe_profile(request.user),
        },
    )


# ============================================================================
# RETURN VIEWS
# ============================================================================


@login_required
def return_list(request):
    """List all return records with search, filters, and pagination."""
    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    order_by = request.GET.get("order_by", "-borrowed_date")
    page = request.GET.get("page")

    context = services.get_return_list_context(
        request.user, search, status_filter, date_from, date_to, order_by, page,
    )
    context["profile"] = get_safe_profile(request.user)
    return render(request, "return/return_list.html", context)


@login_required
def return_create(request, request_id):
    """
    Process return for an approved borrow request (staff or admin).

    Restores equipment stock and sets request status to Returned.
    """
    if not (is_admin_user(request.user) or is_staff_user(request.user)):
        return HttpResponseForbidden("Only staff and admin can process returns.")

    if request.method == "POST":
        due_date_raw = request.POST.get("due_date", "").strip()
        condition_notes = request.POST.get("condition_notes", "").strip()

        if not due_date_raw:
            messages.error(request, "Due date is required.")
            return redirect("create_return", request_id=request_id)

        try:
            due_date = datetime.strptime(due_date_raw, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid due date format.")
            return redirect("create_return", request_id=request_id)

        try:
            services.process_return(request_id, request.user, due_date, condition_notes)
        except BorrowRequest.DoesNotExist:
            messages.error(request, "Borrow request not found.")
            return redirect("borrow_list")
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("borrow_detail", request_id=request_id)
        except Exception:
            logger.exception("Failed to process return for request %s", request_id)
            messages.error(request, "An unexpected error occurred while processing the return.")
            return redirect("borrow_detail", request_id=request_id)

        messages.success(request, "Return processed successfully. Stock restored.")
        return redirect("return_list")

    borrow_request = get_object_or_404(BorrowRequest, request_id=request_id)
    if borrow_request.status != BorrowRequest.STATUS_APPROVED:
        messages.error(request, "Return can only be created for approved borrow requests.")
        return redirect("borrow_detail", request_id=borrow_request.request_id)

    return render(
        request,
        "return/return_form.html",
        {
            "borrow_request": borrow_request,
            "profile": get_safe_profile(request.user),
        },
    )


@login_required
def return_detail(request, transaction_id):
    """View return record details."""
    return_record = services.get_return_detail(transaction_id)
    if return_record is None:
        from django.http import Http404
        raise Http404

    if not (is_admin_user(request.user) or is_staff_user(request.user) or return_record.request.user == request.user):
        return HttpResponseForbidden("You don't have permission to view this return.")

    return render(
        request,
        "return/return_detail.html",
        {
            "return_record": return_record,
            "profile": get_safe_profile(request.user),
        },
    )


# ============================================================================
# REPORTS VIEW
# ============================================================================


@login_required
def reports(request):
    """Generate comprehensive reports."""
    if not (is_admin_user(request.user) or is_staff_user(request.user)):
        return HttpResponseForbidden("Only staff and admin can view reports.")

    period = request.GET.get("period", "all")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    context = services.get_reports_context()
    context["profile"] = get_safe_profile(request.user)
    context["period"] = period
    context["date_from"] = date_from
    context["date_to"] = date_to

    return render(request, "reports/reports.html", context)
