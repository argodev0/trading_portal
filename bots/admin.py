from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import Bot, BotRun


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    """Admin interface for Bot model"""
    
    list_display = [
        'name', 'user', 'strategy', 'pair', 'timeframe', 
        'status', 'is_active', 'current_run_link', 'total_runs', 'created_at'
    ]
    
    list_filter = [
        'strategy', 'status', 'is_active', 'timeframe', 
        'exchange_key__exchange__name', 'created_at'
    ]
    
    search_fields = [
        'name', 'user__username', 'user__email', 'pair',
        'exchange_key__exchange__name'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'current_run_info',
        'bot_statistics', 'formatted_parameters'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'user', 'status', 'is_active')
        }),
        ('Trading Configuration', {
            'fields': ('exchange_key', 'strategy', 'pair', 'timeframe')
        }),
        ('Risk Management', {
            'fields': ('max_daily_trades', 'risk_percentage')
        }),
        ('Strategy Parameters', {
            'fields': ('parameters', 'formatted_parameters'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('current_run_info', 'bot_statistics'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_bots', 'deactivate_bots', 'pause_bots']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'exchange_key__exchange'
        ).prefetch_related('runs')
    
    def current_run_link(self, obj):
        """Link to current bot run if active"""
        current_run = obj.get_current_run()
        if current_run:
            url = reverse('admin:bots_botrun_change', args=[current_run.id])
            return format_html(
                '<a href="{}" style="color: green;">Running ({})</a>',
                url, current_run.duration
            )
        return format_html('<span style="color: gray;">Not running</span>')
    current_run_link.short_description = 'Current Run'
    
    def total_runs(self, obj):
        """Total number of runs for this bot"""
        total = obj.get_total_runs()
        successful = obj.get_successful_runs()
        if total > 0:
            success_rate = (successful / total) * 100
            color = 'green' if success_rate >= 80 else 'orange' if success_rate >= 60 else 'red'
            return format_html(
                '<span style="color: {};">{} ({:.1f}% success)</span>',
                color, total, success_rate
            )
        return '0'
    total_runs.short_description = 'Total Runs'
    
    def current_run_info(self, obj):
        """Information about current run"""
        current_run = obj.get_current_run()
        if current_run:
            return format_html(
                '<strong>Status:</strong> {}<br>'
                '<strong>Started:</strong> {}<br>'
                '<strong>Duration:</strong> {}<br>'
                '<strong>Trades:</strong> {}',
                current_run.status.title(),
                current_run.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                current_run.duration,
                current_run.trades_executed
            )
        return 'No active run'
    current_run_info.short_description = 'Current Run Info'
    
    def bot_statistics(self, obj):
        """Bot performance statistics"""
        total_runs = obj.get_total_runs()
        successful_runs = obj.get_successful_runs()
        
        if total_runs > 0:
            success_rate = (successful_runs / total_runs) * 100
            total_trades = sum(run.trades_executed for run in obj.runs.all())
            total_pnl = sum(run.profit_loss for run in obj.runs.all())
            
            return format_html(
                '<strong>Total Runs:</strong> {}<br>'
                '<strong>Successful Runs:</strong> {} ({:.1f}%)<br>'
                '<strong>Total Trades:</strong> {}<br>'
                '<strong>Total P&L:</strong> {:.8f}',
                total_runs, successful_runs, success_rate, total_trades, total_pnl
            )
        return 'No runs yet'
    bot_statistics.short_description = 'Statistics'
    
    def formatted_parameters(self, obj):
        """Pretty-formatted JSON parameters"""
        if obj.parameters:
            try:
                formatted = json.dumps(obj.parameters, indent=2)
                return format_html('<pre>{}</pre>', formatted)
            except (TypeError, ValueError):
                return str(obj.parameters)
        return 'No parameters set'
    formatted_parameters.short_description = 'Formatted Parameters'
    
    # Admin actions
    def activate_bots(self, request, queryset):
        """Activate selected bots"""
        updated = queryset.update(status='active', is_active=True)
        self.message_user(request, f'{updated} bots were activated.')
    activate_bots.short_description = 'Activate selected bots'
    
    def deactivate_bots(self, request, queryset):
        """Deactivate selected bots"""
        updated = queryset.update(status='inactive', is_active=False)
        self.message_user(request, f'{updated} bots were deactivated.')
    deactivate_bots.short_description = 'Deactivate selected bots'
    
    def pause_bots(self, request, queryset):
        """Pause selected bots"""
        updated = queryset.update(status='paused', is_active=False)
        self.message_user(request, f'{updated} bots were paused.')
    pause_bots.short_description = 'Pause selected bots'


@admin.register(BotRun)
class BotRunAdmin(admin.ModelAdmin):
    """Admin interface for BotRun model"""
    
    list_display = [
        'bot_name', 'bot_user', 'start_time', 'duration_display', 
        'status', 'trades_executed', 'profit_loss_display', 'created_at'
    ]
    
    list_filter = [
        'status', 'start_time', 'bot__strategy', 
        'bot__user', 'bot__exchange_key__exchange__name'
    ]
    
    search_fields = [
        'bot__name', 'bot__user__username', 'bot__user__email',
        'bot__pair', 'error_message'
    ]
    
    readonly_fields = [
        'id', 'start_time', 'created_at', 'updated_at',
        'duration_display', 'formatted_logs', 'bot_info'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'bot', 'bot_info', 'status')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_display')
        }),
        ('Performance', {
            'fields': ('trades_executed', 'profit_loss')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Logs', {
            'fields': ('logs', 'formatted_logs'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['stop_runs', 'mark_as_completed', 'mark_as_failed']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'bot__user', 'bot__exchange_key__exchange'
        )
    
    def bot_name(self, obj):
        """Bot name with link to bot admin"""
        url = reverse('admin:bots_bot_change', args=[obj.bot.id])
        return format_html('<a href="{}">{}</a>', url, obj.bot.name)
    bot_name.short_description = 'Bot'
    bot_name.admin_order_field = 'bot__name'
    
    def bot_user(self, obj):
        """Bot owner username"""
        return obj.bot.user.username
    bot_user.short_description = 'User'
    bot_user.admin_order_field = 'bot__user__username'
    
    def duration_display(self, obj):
        """Formatted duration"""
        duration = obj.duration
        if obj.is_running:
            return format_html('<span style="color: green;">{} (running)</span>', duration)
        return duration
    duration_display.short_description = 'Duration'
    
    def profit_loss_display(self, obj):
        """Colored profit/loss display"""
        pnl = obj.profit_loss
        if pnl > 0:
            return format_html('<span style="color: green;">+{:.8f}</span>', pnl)
        elif pnl < 0:
            return format_html('<span style="color: red;">{:.8f}</span>', pnl)
        return '0.00000000'
    profit_loss_display.short_description = 'P&L'
    profit_loss_display.admin_order_field = 'profit_loss'
    
    def formatted_logs(self, obj):
        """Pretty-formatted logs"""
        if obj.logs:
            try:
                formatted = json.dumps(obj.logs, indent=2)
                return format_html('<pre style="max-height: 300px; overflow-y: auto;">{}</pre>', formatted)
            except (TypeError, ValueError):
                return str(obj.logs)
        return 'No logs'
    formatted_logs.short_description = 'Formatted Logs'
    
    def bot_info(self, obj):
        """Bot configuration info"""
        return format_html(
            '<strong>Strategy:</strong> {}<br>'
            '<strong>Pair:</strong> {}<br>'
            '<strong>Timeframe:</strong> {}<br>'
            '<strong>Exchange:</strong> {}',
            obj.bot.get_strategy_display(),
            obj.bot.pair,
            obj.bot.get_timeframe_display(),
            obj.bot.exchange_key.exchange.name
        )
    bot_info.short_description = 'Bot Configuration'
    
    # Admin actions
    def stop_runs(self, request, queryset):
        """Stop selected running bot runs"""
        stopped = 0
        for run in queryset.filter(end_time__isnull=True):
            run.stop_run(status='cancelled')
            stopped += 1
        self.message_user(request, f'{stopped} runs were stopped.')
    stop_runs.short_description = 'Stop selected runs'
    
    def mark_as_completed(self, request, queryset):
        """Mark selected runs as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} runs were marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_failed(self, request, queryset):
        """Mark selected runs as failed"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} runs were marked as failed.')
    mark_as_failed.short_description = 'Mark as failed'
