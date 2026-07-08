from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("staff", "Staff"),
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

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="staff"
    )

    def __str__(self):
        return self.user.get_full_name()