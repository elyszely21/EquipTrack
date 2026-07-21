import json
import logging
from datetime import datetime

from django.db import transaction
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

from .models import Equipment, BorrowRequest, BorrowRequestItem, ReturnRecord
from accounts.models import UserProfile
from accounts.utils import is_admin_user, is_staff_user


# ============================================================================
# DASHBOARD STATISTICS
# ============================================================================


def get_dashboard_context(user):
    """
    Gather all statistics needed for the main dashboard page.

    Returns:
        dict: context dictionary ready to be merged into the template
        context.  Keys match the variable names expected by
        ``dashboard/index.html``.
    """
    # Equipment catalog counts
    total_equipment = Equipment.objects.count()
    available_equipment = Equipment.objects.filter(
        status=Equipment.STATUS_AVAILABLE,
        quantity_available__gt=0,
    ).count()

    # Units currently checked out (total - available)
    borrowed_units = Equipment.objects.aggregate(
        total=Sum("quantity_total"),
        available=Sum("quantity_available"),
    )
    quantity_total_sum = borrowed_units["total"] or 0
    quantity_available_sum = borrowed_units["available"] or 0
    borrowed_equipment = max(quantity_total_sum - quantity_available_sum, 0)

    # Borrow request statistics
    total_borrow_requests = BorrowRequest.objects.count()
    pending_requests = BorrowRequest.objects.filter(
        status=BorrowRequest.STATUS_PENDING,
    ).count()
    approved_requests = BorrowRequest.objects.filter(
        status=BorrowRequest.STATUS_APPROVED,
    ).count()
    rejected_requests = BorrowRequest.objects.filter(
        status=BorrowRequest.STATUS_REJECTED,
    ).count()
    returned_requests = BorrowRequest.objects.filter(
        status=BorrowRequest.STATUS_RETURNED,
    ).count()
    returned_equipment = returned_requests

    # Return records
    total_returns = ReturnRecord.objects.count()
    completed_returns = ReturnRecord.objects.filter(
        return_date__isnull=False,
    ).count()

    # User statistics
    total_borrowers = UserProfile.objects.filter(
        role=UserProfile.ROLE_BORROWER,
        status=UserProfile.STATUS_ACTIVE,
    ).count()
    total_staff = UserProfile.objects.filter(
        role=UserProfile.ROLE_STAFF,
        status=UserProfile.STATUS_ACTIVE,
    ).count()
    total_admins = UserProfile.objects.filter(
        role=UserProfile.ROLE_ADMIN,
        status=UserProfile.STATUS_ACTIVE,
    ).count()
    pending_staff_count = UserProfile.objects.filter(
        role=UserProfile.ROLE_STAFF,
        status=UserProfile.STATUS_PENDING,
    ).count()

    # Stock alerts
    low_stock_equipment = Equipment.objects.filter(
        quantity_available__lte=5,
        quantity_available__gt=0,
    ).count()
    out_of_stock_equipment = Equipment.objects.filter(
        quantity_available=0,
    ).count()

    # Monthly borrow trend (oldest to newest for charts)
    monthly_borrow_data = []
    now = timezone.now()
    for i in range(5, -1, -1):
        month_start = now - timedelta(days=30 * (i + 1))
        month_end = now - timedelta(days=30 * i)
        count = BorrowRequest.objects.filter(
            request_date__gte=month_start,
            request_date__lt=month_end,
        ).count()
        monthly_borrow_data.append({
            "month": month_end.strftime("%b %Y"),
            "count": count,
        })

    # Equipment by category
    categories = (
        Equipment.objects.values("category")
        .annotate(count=Count("equipment_id"))
        .order_by("-count")[:5]
    )
    category_data = [
        {"category": row["category"], "count": row["count"]}
        for row in categories
    ]

    recent_borrow_requests = (
        BorrowRequest.objects.select_related("user")
        .order_by("-request_date")[:5]
    )
    recent_returns = (
        ReturnRecord.objects.select_related("request", "staff", "request__user")
        .order_by("-borrowed_date")[:5]
    )

    pending_staff = []
    if is_admin_user(user):
        pending_staff = (
            UserProfile.objects.select_related("user")
            .filter(
                role=UserProfile.ROLE_STAFF,
                status=UserProfile.STATUS_PENDING,
            )
            .order_by("user__date_joined")
        )

    return {
        "total_equipment": total_equipment,
        "available_equipment": available_equipment,
        "borrowed_equipment": borrowed_equipment,
        "returned_equipment": returned_equipment,
        "total_borrow_requests": total_borrow_requests,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
        "returned_requests": returned_requests,
        "total_returns": total_returns,
        "completed_returns": completed_returns,
        "total_borrowers": total_borrowers,
        "total_staff": total_staff,
        "total_admins": total_admins,
        "pending_staff_count": pending_staff_count,
        "low_stock_equipment": low_stock_equipment,
        "out_of_stock_equipment": out_of_stock_equipment,
        "monthly_borrow_data_json": json.dumps(monthly_borrow_data),
        "category_data_json": json.dumps(category_data),
        "recent_borrow_requests": recent_borrow_requests,
        "recent_returns": recent_returns,
        "pending_staff": pending_staff,
    }


# ============================================================================
# EQUIPMENT SERVICES
# ============================================================================


def get_equipment_queryset(search="", category_filter="", status_filter="", stock_filter=""):
    """
    Build a filtered ``Equipment`` queryset based on the provided
    search term and filter parameters.
    """
    equipments = Equipment.objects.select_related().all()

    if search:
        equipments = equipments.filter(
            Q(name__icontains=search)
            | Q(category__icontains=search)
            | Q(description__icontains=search)
        )

    if category_filter:
        equipments = equipments.filter(category=category_filter)

    if status_filter:
        equipments = equipments.filter(status=status_filter)

    if stock_filter:
        if stock_filter == "low_stock":
            equipments = equipments.filter(quantity_available__lte=5, quantity_available__gt=0)
        elif stock_filter == "out_of_stock":
            equipments = equipments.filter(quantity_available=0)
        elif stock_filter == "available":
            equipments = equipments.filter(quantity_available__gt=0)

    return equipments


def get_equipment_list_context(search, category_filter, status_filter, stock_filter, order_by, page):
    """
    Prepare the full context dict for the equipment list view.
    Returns a dict with paginated equipments and all filter state.
    """
    equipments = get_equipment_queryset(search, category_filter, status_filter, stock_filter)

    if order_by in ["name", "category", "quantity_total", "quantity_available"]:
        equipments = equipments.order_by(order_by)

    categories = Equipment.objects.values_list("category", flat=True).distinct().order_by("category")
    low_stock_count = Equipment.objects.filter(quantity_available__lte=5, quantity_available__gt=0).count()
    out_of_stock_count = Equipment.objects.filter(quantity_available=0).count()

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(equipments, 10)
    try:
        paginated_equipments = paginator.page(page)
    except PageNotAnInteger:
        paginated_equipments = paginator.page(1)
    except EmptyPage:
        paginated_equipments = paginator.page(paginator.num_pages)

    return {
        "equipments": paginated_equipments,
        "search": search,
        "category_filter": category_filter,
        "status_filter": status_filter,
        "stock_filter": stock_filter,
        "order_by": order_by,
        "categories": categories,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
    }


def get_equipment_detail(equipment_id):
    """
    Return a dict with an equipment instance and its borrow history.

    Returns:
        dict with ``equipment``, ``borrow_requests``, ``borrow_history``.
    """
    from django.shortcuts import get_object_or_404

    equipment = get_object_or_404(Equipment, equipment_id=equipment_id)

    borrow_requests = BorrowRequest.objects.filter(
        items__equipment=equipment,
    ).select_related("user").distinct().order_by("-request_date")

    borrow_history = BorrowRequestItem.objects.filter(
        equipment=equipment,
    ).select_related("request", "request__user").order_by("-request__request_date")

    return {
        "equipment": equipment,
        "borrow_requests": borrow_requests,
        "borrow_history": borrow_history,
    }


# ============================================================================
# INVENTORY SERVICES
# ============================================================================


def get_inventory_list_context(search, category_filter, status_filter, stock_filter, order_by, page):
    """
    Prepare the full context dict for the inventory list view.

    Similar to the equipment list but adds ``borrowed_quantity`` and
    ``stock_status`` for each item (used by the inventory template).
    """
    inventory = get_equipment_queryset(search, category_filter, status_filter, stock_filter)

    if order_by in ["name", "category", "quantity_total", "quantity_available"]:
        inventory = inventory.order_by(order_by)

    categories = Equipment.objects.values_list("category", flat=True).distinct().order_by("category")

    # Calculate borrowed quantity and stock status for each item
    inventory_data = []
    for item in inventory:
        borrowed = item.quantity_total - item.quantity_available
        inventory_data.append({
            "item": item,
            "borrowed_quantity": borrowed,
            "stock_status": item.get_stock_status(),
        })

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(inventory_data, 10)
    try:
        paginated_inventory = paginator.page(page)
    except PageNotAnInteger:
        paginated_inventory = paginator.page(1)
    except EmptyPage:
        paginated_inventory = paginator.page(paginator.num_pages)

    low_stock_count = Equipment.objects.filter(quantity_available__lte=5, quantity_available__gt=0).count()
    out_of_stock_count = Equipment.objects.filter(quantity_available=0).count()

    return {
        "inventory": paginated_inventory,
        "search": search,
        "category_filter": category_filter,
        "status_filter": status_filter,
        "stock_filter": stock_filter,
        "order_by": order_by,
        "categories": categories,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
    }


def get_low_stock_items():
    """
    Return low-stock and out-of-stock equipment querysets.

    Returns:
        tuple: ``(low_stock_items, out_of_stock_items)``
    """
    low_stock_items = Equipment.objects.filter(
        quantity_available__lte=5,
        quantity_available__gt=0,
    ).order_by("quantity_available", "name")

    out_of_stock_items = Equipment.objects.filter(
        quantity_available=0,
    ).order_by("name")

    return low_stock_items, out_of_stock_items


# ============================================================================
# BORROW REQUEST SERVICES
# ============================================================================


def get_borrow_list_context(user, search, status_filter, user_filter, date_from, date_to, order_by, page):
    """
    Prepare the full context dict for the borrow request list view.

    Applies role-based scoping: borrowers only see their own requests.
    """
    try:
        if is_admin_user(user) or is_staff_user(user):
            borrow_requests = BorrowRequest.objects.select_related(
                "user", "approved_by",
            ).prefetch_related("items__equipment").all()
        else:
            borrow_requests = BorrowRequest.objects.select_related(
                "user", "approved_by",
            ).prefetch_related("items__equipment").filter(user=user)
    except Exception:
        logger.exception("get_borrow_list_context: base queryset failed (user=%s)", user.pk)
        raise

    try:
        if search:
            borrow_requests = borrow_requests.filter(
                Q(user__username__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(items__equipment__name__icontains=search)
            ).distinct()
    except Exception:
        logger.exception("get_borrow_list_context: search filter failed")
        raise

    if status_filter:
        borrow_requests = borrow_requests.filter(status=status_filter)

    if user_filter:
        borrow_requests = borrow_requests.filter(user__username__icontains=user_filter)

    if date_from:
        try:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            borrow_requests = borrow_requests.filter(request_date__date__gte=start_date)
        except ValueError:
            pass

    if date_to:
        try:
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            borrow_requests = borrow_requests.filter(request_date__date__lte=end_date)
        except ValueError:
            pass

    if order_by in ["request_date", "-request_date", "status", "user__username"]:
        borrow_requests = borrow_requests.order_by(order_by)

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    try:
        paginator = Paginator(borrow_requests, 10)
        try:
            paginated_requests = paginator.page(page)
        except PageNotAnInteger:
            paginated_requests = paginator.page(1)
        except EmptyPage:
            paginated_requests = paginator.page(paginator.num_pages)
    except Exception:
        logger.exception("get_borrow_list_context: pagination/queryset evaluation failed")
        raise

    return {
        "borrow_requests": paginated_requests,
        "search": search,
        "status_filter": status_filter,
        "user_filter": user_filter,
        "date_from": date_from,
        "date_to": date_to,
        "order_by": order_by,
        "status_choices": BorrowRequest.STATUS_CHOICES,
    }


def get_borrow_detail(request_id):
    """
    Return a borrow request with optimized related objects, or ``None``.
    """
    from django.shortcuts import get_object_or_404

    try:
        return get_object_or_404(
            BorrowRequest.objects.select_related("user", "approved_by")
            .prefetch_related("items__equipment"),
            request_id=request_id,
        )
    except Exception:
        logger.exception("get_borrow_detail: queryset failed (request_id=%s)", request_id)
        raise


def get_available_equipment():
    """
    Return equipment available for borrowing (quantity > 0 and status
    available).
    """
    try:
        return Equipment.objects.filter(
            quantity_available__gt=0,
            status=Equipment.STATUS_AVAILABLE,
        ).order_by("name")
    except Exception:
        logger.exception("get_available_equipment: queryset failed")
        raise


def create_borrow_request(user, equipment_ids, quantities_map):
    """
    Create a new borrow request with line items.

    Validates that each selected equipment is still available and has
    sufficient stock.  Stock is **not** reduced here -- it is decreased
    only on approval.

    Args:
        user: the requesting user.
        equipment_ids: list of equipment ID strings from the form.
        quantities_map: dict mapping equipment_id (str) -> quantity (str).

    Returns:
        BorrowRequest: the newly created request.

    Raises:
        ValueError: if validation fails (no items, invalid data,
        insufficient stock, unavailable equipment).
    """
    if not equipment_ids:
        raise ValueError("Select at least one piece of equipment.")

    seen_ids = set()
    selected_items = []
    for eq_id in equipment_ids:
        raw_qty = quantities_map.get(eq_id, "").strip()
        try:
            equipment_id = int(eq_id)
            quantity = int(raw_qty)
        except (TypeError, ValueError):
            raise ValueError("Invalid equipment or quantity submitted.")

        if equipment_id in seen_ids:
            raise ValueError("Each equipment item can only be selected once.")
        seen_ids.add(equipment_id)

        if quantity < 1:
            raise ValueError("Quantity must be at least 1 for each selected item.")

        selected_items.append((equipment_id, quantity))

    with transaction.atomic():
        borrow_request = BorrowRequest.objects.create(
            user=user,
            status=BorrowRequest.STATUS_PENDING,
        )

        for equipment_id, quantity in selected_items:
            equipment = (
                Equipment.objects.select_for_update()
                .filter(
                    equipment_id=equipment_id,
                    status=Equipment.STATUS_AVAILABLE,
                )
                .first()
            )
            if equipment is None:
                raise ValueError("One or more selected items are no longer available.")

            if quantity > equipment.quantity_available:
                raise ValueError(
                    f"Insufficient stock for {equipment.name}. "
                    f"Only {equipment.quantity_available} available."
                )

            BorrowRequestItem.objects.create(
                request=borrow_request,
                equipment=equipment,
                quantity=quantity,
            )

    return borrow_request


def process_borrow_request(request_id, action, admin_user):
    """
    Approve or reject a pending borrow request.

    Approving atomically decreases stock for each item under row locks.
    Rejecting simply changes the status (stock was never reduced while
    pending).

    Args:
        request_id: the borrow request PK.
        action: ``"approve"`` or ``"reject"``.
        admin_user: the user performing the action.

    Returns:
        BorrowRequest: the updated request.

    Raises:
        BorrowRequest.DoesNotExist: if the request doesn't exist.
        ValueError: if validation fails (not pending, no items,
        insufficient stock, equipment unavailable).
        PermissionError: if action is invalid.
    """
    if action not in ("approve", "reject"):
        raise PermissionError("Invalid action.")

    with transaction.atomic():
        borrow_request = (
            BorrowRequest.objects.select_for_update()
            .prefetch_related("items__equipment")
            .get(request_id=request_id)
        )

        if borrow_request.status != BorrowRequest.STATUS_PENDING:
            raise ValueError("Only pending requests can be approved or rejected.")

        items = list(borrow_request.items.select_related("equipment"))
        if not items:
            raise ValueError("This request has no items and cannot be processed.")

        if action == "approve":
            for item in items:
                equipment = Equipment.objects.select_for_update().get(pk=item.equipment_id)
                if equipment.status != Equipment.STATUS_AVAILABLE:
                    raise ValueError(f"{equipment.name} is not available for borrowing.")
                if item.quantity > equipment.quantity_available:
                    raise ValueError(
                        f"Insufficient stock for {equipment.name}. "
                        f"Only {equipment.quantity_available} available."
                    )
                equipment.quantity_available -= item.quantity
                equipment.save()

            borrow_request.status = BorrowRequest.STATUS_APPROVED
            borrow_request.approved_by = admin_user
            borrow_request.approved_at = timezone.now()
            borrow_request.save(update_fields=["status", "approved_by", "approved_at"])
        else:
            borrow_request.status = BorrowRequest.STATUS_REJECTED
            borrow_request.approved_by = admin_user
            borrow_request.approved_at = timezone.now()
            borrow_request.save(update_fields=["status", "approved_by", "approved_at"])

    return borrow_request


def delete_borrow_request(request_id):
    """
    Delete a pending borrow request.

    Raises:
        ValueError: if the request is not pending.
    """
    from django.shortcuts import get_object_or_404

    borrow_request = get_object_or_404(BorrowRequest, request_id=request_id)

    if borrow_request.status != BorrowRequest.STATUS_PENDING:
        raise ValueError("Only pending requests can be deleted.")

    request_id_display = borrow_request.request_id
    borrow_request.delete()
    return request_id_display


# ============================================================================
# RETURN SERVICES
# ============================================================================


def get_return_list_context(user, search, status_filter, date_from, date_to, order_by, page):
    """
    Prepare the full context dict for the return records list view.

    Applies role-based scoping: borrowers only see their own returns.
    """
    if is_admin_user(user) or is_staff_user(user):
        return_records = ReturnRecord.objects.select_related(
            "request", "staff", "request__user",
        ).all()
    else:
        return_records = ReturnRecord.objects.select_related(
            "request", "staff", "request__user",
        ).filter(request__user=user)

    if search:
        return_records = return_records.filter(
            Q(request__request_id__icontains=search)
            | Q(request__user__username__icontains=search)
            | Q(request__user__first_name__icontains=search)
            | Q(request__user__last_name__icontains=search)
            | Q(staff__username__icontains=search)
        ).distinct()

    if status_filter:
        if status_filter == "completed":
            return_records = return_records.filter(return_date__isnull=False)
        elif status_filter == "pending":
            return_records = return_records.filter(return_date__isnull=True)
        elif status_filter == "late":
            today = timezone.localdate()
            return_records = return_records.filter(
                due_date__lt=today,
                return_date__isnull=True,
            )

    if date_from:
        try:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            return_records = return_records.filter(borrowed_date__gte=start_date)
        except ValueError:
            pass

    if date_to:
        try:
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            return_records = return_records.filter(borrowed_date__lte=end_date)
        except ValueError:
            pass

    if order_by in ["borrowed_date", "-borrowed_date", "due_date", "-due_date", "return_date", "-return_date"]:
        return_records = return_records.order_by(order_by)

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(return_records, 10)
    try:
        paginated_returns = paginator.page(page)
    except PageNotAnInteger:
        paginated_returns = paginator.page(1)
    except EmptyPage:
        paginated_returns = paginator.page(paginator.num_pages)

    return {
        "return_records": paginated_returns,
        "search": search,
        "status_filter": status_filter,
        "date_from": date_from,
        "date_to": date_to,
        "order_by": order_by,
        "today": timezone.localdate(),
    }


def process_return(request_id, staff_user, due_date, condition_notes):
    """
    Process a return for an approved borrow request.

    Restores equipment stock and sets the request status to Returned.

    Args:
        request_id: the borrow request PK.
        staff_user: the staff/admin user processing the return.
        due_date: the due date as a ``date`` object.
        condition_notes: free-text condition notes.

    Returns:
        ReturnRecord: the newly created record.

    Raises:
        ValueError: if the request is not approved or already returned.
        BorrowRequest.DoesNotExist: if the request doesn't exist.
    """
    with transaction.atomic():
        borrow_request = (
            BorrowRequest.objects.select_for_update()
            .prefetch_related("items__equipment")
            .get(request_id=request_id)
        )

        if borrow_request.status != BorrowRequest.STATUS_APPROVED:
            raise ValueError("Return can only be created for approved borrow requests.")

        if hasattr(borrow_request, "return_record"):
            raise ValueError("A return record already exists for this request.")

        for item in borrow_request.items.select_related("equipment"):
            equipment = Equipment.objects.select_for_update().get(pk=item.equipment_id)
            equipment.quantity_available += item.quantity
            if equipment.quantity_available > equipment.quantity_total:
                equipment.quantity_available = equipment.quantity_total
            equipment.save()

        return_record = ReturnRecord.objects.create(
            request=borrow_request,
            staff=staff_user,
            borrowed_date=timezone.localdate(),
            due_date=due_date,
            return_date=timezone.localdate(),
            condition_notes=condition_notes,
        )

        borrow_request.status = BorrowRequest.STATUS_RETURNED
        borrow_request.save(update_fields=["status"])

    return return_record


def get_return_detail(transaction_id):
    """
    Return a ``ReturnRecord`` by transaction ID, or ``None``.
    """
    return ReturnRecord.objects.select_related(
        "request", "staff", "request__user",
    ).filter(transaction_id=transaction_id).first()


# ============================================================================
# REPORTS SERVICES
# ============================================================================


def get_reports_context():
    """
    Gather all statistics needed for the reports page.

    Returns:
        dict: context dictionary with all report data.  Keys match
        the variable names expected by ``reports/reports.html``.
    """
    # Equipment statistics
    total_equipment = Equipment.objects.count()
    available_equipment = Equipment.objects.filter(status=Equipment.STATUS_AVAILABLE).count()
    borrowed_equipment = Equipment.objects.exclude(status=Equipment.STATUS_AVAILABLE).count()

    # Borrow statistics
    total_borrow_requests = BorrowRequest.objects.count()
    pending_requests = BorrowRequest.objects.filter(status=BorrowRequest.STATUS_PENDING).count()
    approved_requests = BorrowRequest.objects.filter(status=BorrowRequest.STATUS_APPROVED).count()
    rejected_requests = BorrowRequest.objects.filter(status=BorrowRequest.STATUS_REJECTED).count()
    returned_requests = BorrowRequest.objects.filter(status=BorrowRequest.STATUS_RETURNED).count()

    # Return statistics
    total_returns = ReturnRecord.objects.count()
    completed_returns = ReturnRecord.objects.filter(return_date__isnull=False).count()

    # User statistics
    total_borrowers = UserProfile.objects.filter(
        role=UserProfile.ROLE_BORROWER, status=UserProfile.STATUS_ACTIVE,
    ).count()
    total_staff = UserProfile.objects.filter(
        role=UserProfile.ROLE_STAFF, status=UserProfile.STATUS_ACTIVE,
    ).count()
    total_admins = UserProfile.objects.filter(
        role=UserProfile.ROLE_ADMIN, status=UserProfile.STATUS_ACTIVE,
    ).count()

    # Most borrowed equipment
    most_borrowed_equipment = (
        BorrowRequestItem.objects.values(
            "equipment__name",
            "equipment__equipment_id",
        )
        .annotate(count=Count("request_item_id"))
        .order_by("-count")[:5]
    )

    # Most active borrowers
    most_active_borrowers = (
        BorrowRequest.objects.values(
            "user__username",
            "user__first_name",
            "user__last_name",
        )
        .annotate(count=Count("request_id"))
        .order_by("-count")[:5]
    )

    # Category statistics
    category_stats = Equipment.objects.values("category").annotate(
        total=Sum("quantity_total"),
        available=Sum("quantity_available"),
    ).order_by("-total")

    # Monthly borrow trend
    monthly_borrow_data = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)
        count = BorrowRequest.objects.filter(
            request_date__range=[month_start, month_end],
        ).count()
        monthly_borrow_data.append({
            "month": month_start.strftime("%b %Y"),
            "count": count,
        })

    # Stock alerts
    low_stock_count = Equipment.objects.filter(
        quantity_available__lte=5, quantity_available__gt=0,
    ).count()
    out_of_stock_count = Equipment.objects.filter(quantity_available=0).count()

    return {
        "equipment_count": total_equipment,
        "available_equipment": available_equipment,
        "borrowed_equipment": borrowed_equipment,
        "borrow_count": total_borrow_requests,
        "pending_count": pending_requests,
        "approved_count": approved_requests,
        "rejected_count": rejected_requests,
        "returned_count": returned_requests,
        "return_count": total_returns,
        "completed_return_count": completed_returns,
        "staff_count": total_staff,
        "borrower_count": total_borrowers,
        "admin_count": total_admins,
        "most_borrowed_equipment": most_borrowed_equipment,
        "most_active_borrowers": most_active_borrowers,
        "category_stats": category_stats,
        "monthly_borrow_data_json": json.dumps(monthly_borrow_data),
        "category_data_json": json.dumps(list(category_stats)),
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
    }
