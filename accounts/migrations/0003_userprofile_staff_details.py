from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_userprofile_status_and_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="department",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="position",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
