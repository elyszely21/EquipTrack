from django.contrib import admin
from .models import Equipment, BorrowRequest, BorrowRequestItem, ReturnRecord, AuditLog


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_id', 'name', 'category', 'quantity_total', 'quantity_available', 'status']
    list_filter = ['status', 'category']
    search_fields = ['name', 'category', 'description']
    ordering = ['name']
    readonly_fields = ['equipment_id']


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'user', 'request_date', 'status', 'approved_by']
    list_filter = ['status', 'request_date']
    search_fields = ['user__username', 'user__email', 'request_id']
    ordering = ['-request_date']
    readonly_fields = ['request_id', 'request_date', 'approved_at']


@admin.register(BorrowRequestItem)
class BorrowRequestItemAdmin(admin.ModelAdmin):
    list_display = ['request_item_id', 'request', 'equipment', 'quantity']
    list_filter = ['equipment']
    search_fields = ['equipment__name', 'request__request_id']
    ordering = ['request']


@admin.register(ReturnRecord)
class ReturnRecordAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'request', 'staff', 'borrowed_date', 'due_date', 'return_date']
    list_filter = ['borrowed_date', 'due_date', 'return_date']
    search_fields = ['request__request_id', 'staff__username']
    ordering = ['-borrowed_date']
    readonly_fields = ['transaction_id']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description', 'action']
    ordering = ['-timestamp']
    readonly_fields = ['log_id', 'timestamp']
