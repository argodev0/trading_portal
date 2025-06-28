from django.contrib import admin
from .models import Exchange, UserAPIKey


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    """Admin configuration for Exchange model"""
    
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(UserAPIKey)
class UserAPIKeyAdmin(admin.ModelAdmin):
    """Admin configuration for UserAPIKey model"""
    
    list_display = ('user', 'exchange', 'name', 'api_key_public_part', 'is_active', 'created_at')
    list_filter = ('exchange', 'is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'exchange__name', 'name', 'api_key_public_part')
    list_select_related = ('user', 'exchange')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'exchange', 'name', 'is_active')
        }),
        ('API Credentials', {
            'fields': ('api_key_public_part', 'encrypted_credentials', 'nonce'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make encrypted_credentials and nonce read-only after creation for security
        if obj:  # Editing existing object
            return self.readonly_fields + ('encrypted_credentials', 'nonce')
        return self.readonly_fields
