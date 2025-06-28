from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin configuration"""
    
    # Fields to display in the admin list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'account_tier', 'is_staff', 'date_joined')
    
    # Filters for the admin list view
    list_filter = ('account_tier', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    # Fields to search in admin
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Ordering in admin list view
    ordering = ('-date_joined',)
    
    # Add account_tier to the fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Account Information', {
            'fields': ('account_tier',)
        }),
    )
    
    # Add account_tier to the add form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Account Information', {
            'fields': ('account_tier',)
        }),
    )
