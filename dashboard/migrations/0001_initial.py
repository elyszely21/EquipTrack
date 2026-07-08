import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Equipment",
            fields=[
                ("equipment_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=150)),
                ("category", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("quantity_total", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ("quantity_available", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ("status", models.CharField(choices=[("available", "Available"), ("unavailable", "Unavailable"), ("maintenance", "Maintenance")], default="available", max_length=20)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="BorrowRequest",
            fields=[
                ("request_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("request_date", models.DateTimeField(default=django.utils.timezone.now)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("returned", "Returned")], default="pending", max_length=20)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_borrow_requests", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="borrow_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-request_date"],
            },
        ),
        migrations.CreateModel(
            name="BorrowRequestItem",
            fields=[
                ("request_item_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("quantity", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("equipment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="request_items", to="dashboard.equipment")),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="dashboard.borrowrequest")),
            ],
            options={
                "unique_together": {("request", "equipment")},
            },
        ),
        migrations.CreateModel(
            name="ReturnRecord",
            fields=[
                ("transaction_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("borrowed_date", models.DateField(default=django.utils.timezone.localdate)),
                ("due_date", models.DateField()),
                ("return_date", models.DateField(blank=True, null=True)),
                ("condition_notes", models.TextField(blank=True)),
                ("request", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="return_record", to="dashboard.borrowrequest")),
                ("staff", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="processed_returns", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-borrowed_date"],
            },
        ),
    ]
