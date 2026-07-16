from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from accounts.utils import is_admin_user, is_staff_user, is_borrower_user


__all__ = ["is_admin_user", "is_staff_user", "is_borrower_user", "paginate_queryset"]


def paginate_queryset(request, queryset, per_page=10):
    """
    Paginate *queryset* based on the ``page`` GET parameter.

    Returns:
        Page: a Django ``Page`` object (handles invalid / missing values
        gracefully).
    """
    paginator = Paginator(queryset, per_page)
    page = request.GET.get("page")

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
