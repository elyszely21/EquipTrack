from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q

from .models import UserProfile, Staff


def register_user(cleaned_data):
    """
    Create a new User and configure their UserProfile.

    Staff applicants are placed in ``STATUS_PENDING`` so an admin must
    approve them before they can log in.  Borrowers are activated
    immediately.

    Returns:
        User: the newly created user instance.
    """
    user = User.objects.create_user(
        username=cleaned_data["username"],
        first_name=cleaned_data["first_name"],
        last_name=cleaned_data["last_name"],
        email=cleaned_data["email"],
        password=cleaned_data["password"],
    )

    profile = user.profile
    profile.middle_name = cleaned_data["middle_name"]
    profile.suffix = cleaned_data["suffix"]
    profile.contact_number = cleaned_data["contact_number"]
    profile.department = cleaned_data["department"]
    profile.position = cleaned_data["position"]
    profile.role = cleaned_data["role"]
    profile.status = (
        UserProfile.STATUS_PENDING
        if profile.role == UserProfile.ROLE_STAFF
        else UserProfile.STATUS_ACTIVE
    )
    profile.save()

    return user


def authenticate_user(username, password):
    """
    Authenticate credentials and return ``(user, profile)`` or
    ``(None, None)`` on failure.

    Also ensures a ``UserProfile`` exists (handles legacy users created
    before the signal was in place).

    Returns:
        tuple: ``(User, UserProfile)`` or ``(None, None)``.
    """
    user = authenticate(username=username, password=password)
    if user is None:
        return None, None

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "contact_number": "",
            "role": UserProfile.ROLE_ADMIN if user.is_superuser else UserProfile.ROLE_BORROWER,
            "status": UserProfile.STATUS_ACTIVE,
        },
    )
    return user, profile


def get_pending_staff_profiles():
    """
    Return all staff profiles ordered by approval status and join date.
    Used on the admin staff-approval page.
    """
    return (
        UserProfile.objects
        .select_related("user")
        .filter(role=UserProfile.ROLE_STAFF)
        .order_by("status", "user__date_joined")
    )


def approve_staff_registration(profile_id):
    """
    Approve a pending staff profile: set status to ``ACTIVE`` and
    create a ``Staff`` management record.

    Returns:
        UserProfile or None: the profile if found, else ``None``.
    """
    profile = UserProfile.objects.filter(
        id=profile_id,
        role=UserProfile.ROLE_STAFF,
        status=UserProfile.STATUS_PENDING,
    ).first()

    if profile is None:
        return None

    profile.status = UserProfile.STATUS_ACTIVE
    profile.save(update_fields=["status"])

    Staff.objects.get_or_create(
        user_profile=profile,
        defaults={"department": profile.department or "General"},
    )

    return profile


def reject_staff_registration(profile_id):
    """
    Reject a pending staff profile by setting status to ``REJECTED``.

    Returns:
        UserProfile or None: the profile if found, else ``None``.
    """
    profile = UserProfile.objects.filter(
        id=profile_id,
        role=UserProfile.ROLE_STAFF,
        status=UserProfile.STATUS_PENDING,
    ).first()

    if profile is None:
        return None

    profile.status = UserProfile.STATUS_REJECTED
    profile.save(update_fields=["status"])

    return profile


def get_staff_list(search=""):
    """
    Return all ``Staff`` records, optionally filtered by *search*
    (matches first name, last name, username, or department).
    """
    staff = Staff.objects.select_related(
        "user_profile",
        "user_profile__user",
    ).all()

    if search:
        staff = staff.filter(
            Q(user_profile__user__first_name__icontains=search)
            | Q(user_profile__user__last_name__icontains=search)
            | Q(user_profile__user__username__icontains=search)
            | Q(department__icontains=search)
            | Q(user_profile__department__icontains=search)
        )

    return staff


def get_staff_detail(pk):
    """
    Return a single ``Staff`` record by PK with optimized selects,
    or ``None`` if not found.
    """
    return Staff.objects.select_related(
        "user_profile", "user_profile__user"
    ).filter(pk=pk).first()


def update_user_profile(user, cleaned_data):
    """
    Update both the ``User`` fields (first_name, last_name, email) and
    the linked ``UserProfile`` fields from form cleaned data.
    """
    user.first_name = cleaned_data.get("first_name", user.first_name)
    user.last_name = cleaned_data.get("last_name", user.last_name)
    user.email = cleaned_data.get("email", user.email)
    user.save()

    profile = user.profile
    profile.middle_name = cleaned_data.get("middle_name", profile.middle_name)
    profile.suffix = cleaned_data.get("suffix", profile.suffix)
    profile.contact_number = cleaned_data.get("contact_number", profile.contact_number)
    profile.department = cleaned_data.get("department", profile.department)
    profile.position = cleaned_data.get("position", profile.position)
    profile.save()
