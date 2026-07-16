from django.contrib import admin
from django.utils.html import format_html
from .models import Equipment, BorrowRequest, BorrowRequestItem, ReturnRecord


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('equipment_id', 'name', 'category', 'quantity_total', 'quantity_available', 'status', 'get_stock_status')
    list_filter = ('category', 'status')
    search_fields = ('name', 'category', 'description')
    list_editable = ('status',)
    ordering = ('name',)
    
    def get_stock_status(self, obj):
        if obj.quantity_available == 0:
            return format_html('<span style="color: red; font-weight: bold;">Out of Stock</span>')
        elif obj.quantity_available <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">Low Stock</span>')
        else:
            return format_html('<span style="color: green;">OK</span>')
    get_stock_status.short_description = "Stock Status"


class BorrowRequestItemInline(admin.TabularInline):
    model = BorrowRequestItem
    extra = 1
    readonly_fields = ('request_item_id',)


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'user', 'request_date', 'status', 'approved_by', 'approved_at')
    list_filter = ('status', 'request_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'status')
    list_select_related = ('user', 'approved_by')
    inlines = [BorrowRequestItemInline]
    ordering = ('-request_date',)
    readonly_fields = ('request_id', 'request_date')


@admin.register(BorrowRequestItem)
class BorrowRequestItemAdmin(admin.ModelAdmin):
    list_display = ('request_item_id', 'request', 'equipment', 'quantity')
    list_filter = ('equipment__category',)
    search_fields = ('request__request_id', 'equipment__name')
    list_select_related = ('request', 'equipment')
    ordering = ('request', 'equipment')


@admin.register(ReturnRecord)
class ReturnRecordAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'request', 'staff', 'borrowed_date', 'due_date', 'return_date', 'condition_notes')
    list_filter = ('borrowed_date', 'return_date', 'due_date')
    search_fields = ('request__request_id', 'staff__username', 'condition_notes')
    list_select_related = ('request', 'staff')
    ordering = ('-borrowed_date',)
    readonly_fields = ('transaction_id', 'borrowed_date')
