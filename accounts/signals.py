from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:

        role = UserProfile.ROLE_ADMIN if instance.is_superuser else UserProfile.ROLE_BORROWER

        UserProfile.objects.create(
            user=instance,
            contact_number="",
            role=role,
            status=UserProfile.STATUS_ACTIVE
        )


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):

    instance.profile.save()
