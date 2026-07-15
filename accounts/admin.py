from django.contrib import admin
from .models import UserProfile, Staff


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'status', 'contact_number', 'department']
    list_filter = ['role', 'status']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['user__username']
    readonly_fields = ['user']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'user_profile', 'department', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['user_profile__user__username', 'user_profile__user__email', 'department']
    ordering = ['user_profile__user__last_name']
    readonly_fields = ['staff_id', 'created_at', 'updated_at']
