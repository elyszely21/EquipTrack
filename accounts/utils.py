from .models import UserProfile


def is_admin_user(user):
    """Check if user has an active admin profile."""
    return (
        user.is_authenticated
        and hasattr(user, "profile")
        and user.profile.role == UserProfile.ROLE_ADMIN
        and user.profile.status == UserProfile.STATUS_ACTIVE
    )


def is_staff_user(user):
    """Check if user has an active staff profile."""
    return (
        user.is_authenticated
        and hasattr(user, "profile")
        and user.profile.role == UserProfile.ROLE_STAFF
        and user.profile.status == UserProfile.STATUS_ACTIVE
    )


def is_borrower_user(user):
    """Check if user has an active borrower profile."""
    return (
        user.is_authenticated
        and hasattr(user, "profile")
        and user.profile.role == UserProfile.ROLE_BORROWER
        and user.profile.status == UserProfile.STATUS_ACTIVE
    )
