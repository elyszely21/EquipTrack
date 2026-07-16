from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Staff


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    filter_horizontal = ()
    fields = ('middle_name', 'suffix', 'contact_number', 'department', 'position', 'role', 'status')
    readonly_fields = ()


class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name_plural = "Staff Details"
    fields = ('department', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'get_role', 'get_status')
    list_select_related = ('profile',)
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else "-"
    get_role.short_description = "Role"
    
    def get_status(self, obj):
        return obj.profile.status if hasattr(obj, 'profile') else "-"
    get_status.short_description = "Status"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'department', 'position', 'contact_number')
    list_filter = ('role', 'status', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'contact_number', 'department')
    list_select_related = ('user',)
    ordering = ('user__last_name', 'user__first_name')


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'user_profile', 'department', 'created_at', 'updated_at')
    list_filter = ('department', 'created_at')
    search_fields = ('user_profile__user__username', 'user_profile__user__first_name', 'user_profile__user__last_name', 'department')
    list_select_related = ('user_profile__user',)
    ordering = ('user_profile__user__last_name',)
    readonly_fields = ('staff_id', 'created_at', 'updated_at')


# Unregister default User admin and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
