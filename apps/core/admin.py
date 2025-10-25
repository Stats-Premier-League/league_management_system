# DJANGO ADMIN CONFIGURATION 
# Main Purpose: This file registers and customizes the appearance and behavior
# of the custom User model within the Django Administration site. It ensures
# that the project's additional user fields (like role, phone, and team)
# are visible and editable by administrators, enhancing the functionality of the
# built-in admin interface.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('League Information', {
            'fields': ('role', 'phone', 'date_of_birth', 'profile_picture', 'team')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('League Information', {
            'fields': ('role', 'phone', 'date_of_birth')
        }),
    )