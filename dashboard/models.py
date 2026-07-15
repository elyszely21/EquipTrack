from django.conf import settings
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validate_image_size(value):
    """Validate that image file size is not greater than 2MB"""
    filesize = value.size
    max_size = 2 * 1024 * 1024  # 2MB
    if filesize > max_size:
        raise ValidationError("The maximum file size that can be uploaded is 2MB.")


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
    image = models.ImageField(
        upload_to='equipment_images/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size,
        ],
        help_text='Upload equipment image (JPEG/PNG, max 2MB)'
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['name']),
            models.Index(fields=['quantity_available']),
            models.Index(fields=['quantity_total']),
            models.Index(fields=['status', 'category']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.quantity_available > self.quantity_total:
            self.quantity_available = self.quantity_total

        # Auto-update status based on availability
        # Only update if not explicitly in maintenance
        if self.status != self.STATUS_MAINTENANCE:
            if self.quantity_available == 0:
                self.status = self.STATUS_UNAVAILABLE
            elif self.quantity_available > 0:
                self.status = self.STATUS_AVAILABLE

        super().save(*args, **kwargs)

    def is_low_stock(self):
        """Check if equipment is low stock (≤5 items)"""
        return self.quantity_available <= 5 and self.quantity_available > 0

    def is_out_of_stock(self):
        """Check if equipment is out of stock"""
        return self.quantity_available == 0

    def get_stock_status(self):
        """Get human-readable stock status"""
        if self.is_out_of_stock():
            return "Out of Stock"
        elif self.is_low_stock():
            return "Low Stock"
        else:
            return "In Stock"

    def get_stock_status_class(self):
        """Get Bootstrap class for stock status badge"""
        if self.is_out_of_stock():
            return "danger"
        elif self.is_low_stock():
            return "warning text-dark"
        else:
            return "success"


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
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['request_date']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'request_date']),
            models.Index(fields=['status', 'request_date']),
        ]

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
        indexes = [
            models.Index(fields=['request']),
            models.Index(fields=['equipment']),
            models.Index(fields=['request', 'equipment']),
        ]

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
        indexes = [
            models.Index(fields=['request']),
            models.Index(fields=['staff']),
            models.Index(fields=['borrowed_date']),
            models.Index(fields=['return_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['staff', 'borrowed_date']),
        ]

    def __str__(self):
        return f"Return Record #{self.transaction_id}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("borrow_created", "Borrow Request Created"),
        ("borrow_approved", "Borrow Request Approved"),
        ("borrow_rejected", "Borrow Request Rejected"),
        ("borrow_cancelled", "Borrow Request Cancelled"),
        ("borrow_returned", "Equipment Returned"),
        ("equipment_created", "Equipment Added"),
        ("equipment_updated", "Equipment Updated"),
        ("equipment_deleted", "Equipment Deleted"),
        ("staff_approved", "Staff Account Approved"),
        ("staff_rejected", "Staff Account Rejected"),
        ("profile_updated", "Profile Updated"),
        ("login", "User Login"),
        ("logout", "User Logout"),
    ]

    log_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    related_model = models.CharField(max_length=100, blank=True)
    related_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.user.username if self.user else 'System'} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
