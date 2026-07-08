from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Equipment(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_UNAVAILABLE = "unavailable"
    STATUS_MAINTENANCE = "maintenance"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_UNAVAILABLE, "Unavailable"),
        (STATUS_MAINTENANCE, "Maintenance"),
    ]

    equipment_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity_total = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    quantity_available = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.quantity_available > self.quantity_total:
            self.quantity_available = self.quantity_total

        if self.quantity_available == 0 and self.status == self.STATUS_AVAILABLE:
            self.status = self.STATUS_UNAVAILABLE

        super().save(*args, **kwargs)


class BorrowRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_RETURNED = "returned"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_RETURNED, "Returned"),
    ]

    request_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrow_requests",
    )
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_borrow_requests",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-request_date"]

    def __str__(self):
        return f"Request #{self.request_id} - {self.user.username}"


class BorrowRequestItem(models.Model):
    request_item_id = models.BigAutoField(primary_key=True)
    request = models.ForeignKey(
        BorrowRequest,
        on_delete=models.CASCADE,
        related_name="items",
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="request_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ("request", "equipment")

    def __str__(self):
        return f"{self.equipment.name} x {self.quantity}"


class ReturnRecord(models.Model):
    transaction_id = models.BigAutoField(primary_key=True)
    request = models.OneToOneField(
        BorrowRequest,
        on_delete=models.CASCADE,
        related_name="return_record",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="processed_returns",
    )
    borrowed_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    condition_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-borrowed_date"]

    def __str__(self):
        return f"Return Record #{self.transaction_id}"
