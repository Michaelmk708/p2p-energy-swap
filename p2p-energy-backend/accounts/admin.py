from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Use BaseUserAdmin's fieldsets as-is to avoid duplicate fields like 'email'
    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = BaseUserAdmin.add_fieldsets

    list_display = ("id", "email", "username", "is_staff", "is_active")
    ordering = ("id",)
    search_fields = ("email", "username")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "phone", "timezone", "created_at")
    search_fields = ("user__email", "user__username", "phone")
    list_filter = ("role", "timezone")
