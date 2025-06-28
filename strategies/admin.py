"""
Admin configuration for strategies app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import GeneratedStrategy, StrategyGenerationLog


@admin.register(GeneratedStrategy)
class GeneratedStrategyAdmin(admin.ModelAdmin):
    """Admin interface for GeneratedStrategy model."""
    
    list_display = [
        'name', 'user_email', 'strategy_type', 'status', 
        'usage_count', 'is_public', 'created_at'
    ]
    
    list_filter = [
        'status', 'strategy_type', 'is_public', 'ai_model_version',
        'created_at', 'updated_at'
    ]
    
    search_fields = [
        'name', 'description', 'original_prompt', 
        'user__email', 'user__first_name', 'user__last_name'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'usage_count',
        'formatted_code', 'formatted_validation_results',
        'generation_logs_link'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'description', 'strategy_type')
        }),
        ('Generation Details', {
            'fields': ('original_prompt', 'ai_model_version', 'generation_metadata')
        }),
        ('Generated Code', {
            'fields': ('formatted_code', 'generated_code'),
            'description': 'AI-generated strategy code'
        }),
        ('Validation & Status', {
            'fields': ('status', 'formatted_validation_results', 'validation_results')
        }),
        ('Configuration', {
            'fields': ('parameters', 'performance_metrics'),
            'classes': ('collapse',)
        }),
        ('Usage & Sharing', {
            'fields': ('usage_count', 'is_public', 'generation_logs_link')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        """Display user email with link to user admin."""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def formatted_code(self, obj):
        """Display formatted code in admin."""
        if obj.generated_code:
            return format_html(
                '<pre style="max-height: 300px; overflow-y: auto; '
                'background: #f8f8f8; padding: 10px; font-size: 12px;">{}</pre>',
                obj.generated_code[:2000] + ('...' if len(obj.generated_code) > 2000 else '')
            )
        return '-'
    formatted_code.short_description = 'Generated Code (Preview)'
    
    def formatted_validation_results(self, obj):
        """Display formatted validation results."""
        if obj.validation_results:
            valid = obj.validation_results.get('valid', False)
            color = 'green' if valid else 'red'
            status = 'Valid' if valid else 'Invalid'
            
            details = []
            if 'errors' in obj.validation_results:
                details.append(f"Errors: {len(obj.validation_results['errors'])}")
            if 'warnings' in obj.validation_results:
                details.append(f"Warnings: {len(obj.validation_results['warnings'])}")
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span><br><small>{}</small>',
                color, status, ' | '.join(details)
            )
        return '-'
    formatted_validation_results.short_description = 'Validation Status'
    
    def generation_logs_link(self, obj):
        """Link to related generation logs."""
        count = obj.generation_logs.count()
        if count > 0:
            url = reverse('admin:strategies_strategygenerationlog_changelist')
            return format_html(
                '<a href="{}?strategy__id__exact={}">{} logs</a>',
                url, obj.id, count
            )
        return 'No logs'
    generation_logs_link.short_description = 'Generation Logs'
    
    actions = ['mark_as_validated', 'mark_as_active', 'mark_as_archived']
    
    def mark_as_validated(self, request, queryset):
        """Mark selected strategies as validated."""
        updated = queryset.update(status='validated')
        self.message_user(request, f'{updated} strategies marked as validated.')
    mark_as_validated.short_description = 'Mark selected strategies as validated'
    
    def mark_as_active(self, request, queryset):
        """Mark selected strategies as active."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} strategies marked as active.')
    mark_as_active.short_description = 'Mark selected strategies as active'
    
    def mark_as_archived(self, request, queryset):
        """Mark selected strategies as archived."""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} strategies marked as archived.')
    mark_as_archived.short_description = 'Mark selected strategies as archived'


@admin.register(StrategyGenerationLog)
class StrategyGenerationLogAdmin(admin.ModelAdmin):
    """Admin interface for StrategyGenerationLog model."""
    
    list_display = [
        'created_at', 'user_email', 'status', 'ai_model_used',
        'processing_time', 'has_strategy', 'tokens_used'
    ]
    
    list_filter = [
        'status', 'ai_model_used', 'created_at'
    ]
    
    search_fields = [
        'prompt', 'error_message', 'user__email'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'processing_time_seconds',
        'formatted_prompt', 'formatted_response', 'formatted_code'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'created_at', 'status', 'ai_model_used')
        }),
        ('Generation Request', {
            'fields': ('formatted_prompt', 'prompt')
        }),
        ('AI Response', {
            'fields': ('formatted_response', 'ai_response_raw'),
            'classes': ('collapse',)
        }),
        ('Extracted Code', {
            'fields': ('formatted_code', 'extracted_code'),
            'classes': ('collapse',)
        }),
        ('Results & Metrics', {
            'fields': ('strategy', 'error_message', 'processing_time_seconds', 'tokens_used')
        })
    )
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def processing_time(self, obj):
        """Display formatted processing time."""
        if obj.processing_time_seconds:
            return f"{obj.processing_time_seconds:.2f}s"
        return '-'
    processing_time.short_description = 'Processing Time'
    processing_time.admin_order_field = 'processing_time_seconds'
    
    def has_strategy(self, obj):
        """Display whether a strategy was created."""
        if obj.strategy:
            url = reverse('admin:strategies_generatedstrategy_change', args=[obj.strategy.pk])
            return format_html('<a href="{}">✓ {}</a>', url, obj.strategy.name)
        return '✗ No strategy'
    has_strategy.short_description = 'Strategy Created'
    
    def formatted_prompt(self, obj):
        """Display formatted prompt."""
        if obj.prompt:
            return format_html(
                '<div style="max-height: 150px; overflow-y: auto; '
                'background: #f8f8f8; padding: 8px; font-size: 12px;">{}</div>',
                obj.prompt[:1000] + ('...' if len(obj.prompt) > 1000 else '')
            )
        return '-'
    formatted_prompt.short_description = 'Prompt (Preview)'
    
    def formatted_response(self, obj):
        """Display formatted AI response."""
        if obj.ai_response_raw:
            return format_html(
                '<pre style="max-height: 200px; overflow-y: auto; '
                'background: #f8f8f8; padding: 8px; font-size: 11px;">{}</pre>',
                obj.ai_response_raw[:1500] + ('...' if len(obj.ai_response_raw) > 1500 else '')
            )
        return '-'
    formatted_response.short_description = 'AI Response (Preview)'
    
    def formatted_code(self, obj):
        """Display formatted extracted code."""
        if obj.extracted_code:
            return format_html(
                '<pre style="max-height: 200px; overflow-y: auto; '
                'background: #f0f0f0; padding: 8px; font-size: 11px;">{}</pre>',
                obj.extracted_code[:1500] + ('...' if len(obj.extracted_code) > 1500 else '')
            )
        return '-'
    formatted_code.short_description = 'Extracted Code (Preview)'
