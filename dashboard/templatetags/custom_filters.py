from django import template

register = template.Library()


@register.filter
def percentage_of(value, total):
    """
    Calculate percentage of value relative to total.
    Usage: {{ value|percentage_of:total }}
    """
    try:
        if total == 0:
            return 0
        return int((float(value) / float(total)) * 100)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0