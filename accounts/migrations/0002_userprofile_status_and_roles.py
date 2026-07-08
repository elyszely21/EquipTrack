# Generated for EquipTrack authentication role workflow.

from django.db import migrations, models


def activate_existing_superusers(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("accounts", "UserProfile")

    for user in User.objects.filter(is_superuser=True):
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "contact_number": "",
                "role": "admin",
                "status": "active",
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[
                    ("borrower", "Borrower"),
                    ("staff", "Staff"),
                    ("admin", "Admin"),
                ],
                default="borrower",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("active", "Active"),
                    ("rejected", "Rejected"),
                ],
                default="active",
                max_length=20,
            ),
        ),
        migrations.RunPython(activate_existing_superusers, migrations.RunPython.noop),
    ]
