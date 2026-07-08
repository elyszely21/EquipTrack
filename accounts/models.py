from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_BORROWER = "borrower"
    ROLE_STAFF = "staff"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_BORROWER, "Borrower"),
        (ROLE_STAFF, "Staff"),
        (ROLE_ADMIN, "Admin"),
    ]

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True
    )

    suffix = models.CharField(
        max_length=20,
        blank=True
    )

    contact_number = models.CharField(
        max_length=20
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )

    position = models.CharField(
        max_length=100,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_BORROWER
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)

    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="staff"
    )

    department = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user_profile__user__last_name"]

    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} ({self.department})"




