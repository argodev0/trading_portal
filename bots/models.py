from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Bot(models.Model):
    """
    Model representing a trading bot configuration
    """
    
    STRATEGY_CHOICES = [
        ('grid', 'Grid Trading'),
        ('dca', 'Dollar Cost Averaging'),
        ('scalping', 'Scalping'),
        ('momentum', 'Momentum Trading'),
        ('mean_reversion', 'Mean Reversion'),
        ('arbitrage', 'Arbitrage'),
        ('custom', 'Custom Strategy'),
    ]
    
    TIMEFRAME_CHOICES = [
        ('1m', '1 Minute'),
        ('5m', '5 Minutes'),
        ('15m', '15 Minutes'),
        ('30m', '30 Minutes'),
        ('1h', '1 Hour'),
        ('4h', '4 Hours'),
        ('1d', '1 Day'),
        ('1w', '1 Week'),
    ]
    
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=100,
        help_text='User-friendly name for the bot'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bots',
        help_text='User who owns this bot'
    )
    
    exchange_key = models.ForeignKey(
        'exchanges.UserAPIKey',
        on_delete=models.CASCADE,
        related_name='bots',
        help_text='API key to use for trading on the exchange'
    )
    
    strategy = models.CharField(
        max_length=20,
        choices=STRATEGY_CHOICES,
        help_text='Trading strategy to use'
    )
    
    pair = models.CharField(
        max_length=20,
        help_text='Trading pair (e.g., BTC/USDT, ETH/BTC)'
    )
    
    timeframe = models.CharField(
        max_length=5,
        choices=TIMEFRAME_CHOICES,
        default='1h',
        help_text='Timeframe for strategy execution'
    )
    
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text='Strategy-specific parameters (JSON format)'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='inactive',
        help_text='Current status of the bot'
    )
    
    is_active = models.BooleanField(
        default=False,
        help_text='Whether the bot is currently running'
    )
    
    max_daily_trades = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of trades per day'
    )
    
    risk_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.01)],
        help_text='Risk percentage per trade (0.01-100.00)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bot'
        verbose_name_plural = 'Bots'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'], 
                name='unique_bot_name_per_user'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user.username}) - {self.strategy}"
    
    def clean(self):
        """Validate bot configuration"""
        from django.core.exceptions import ValidationError
        
        # Ensure the exchange_key belongs to the same user
        if self.exchange_key and self.exchange_key.user != self.user:
            raise ValidationError(
                'Exchange key must belong to the same user as the bot'
            )
    
    def get_current_run(self):
        """Get the current active run for this bot"""
        return self.runs.filter(end_time__isnull=True).first()
    
    def get_total_runs(self):
        """Get total number of runs for this bot"""
        return self.runs.count()
    
    def get_successful_runs(self):
        """Get number of successful runs"""
        return self.runs.filter(status='completed').count()
    
    def get_success_rate(self):
        """Get success rate as a percentage"""
        total = self.get_total_runs()
        if total == 0:
            return 0.0
        return (self.get_successful_runs() / total) * 100
    
    def has_active_runs(self):
        """Check if the bot has currently running instances"""
        return self.runs.filter(end_time__isnull=True).exists()


class BotRun(models.Model):
    """
    Model to log each bot execution session
    """
    
    STATUS_CHOICES = [
        ('starting', 'Starting'),
        ('running', 'Running'),
        ('stopping', 'Stopping'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    bot = models.ForeignKey(
        Bot,
        on_delete=models.CASCADE,
        related_name='runs',
        help_text='Bot that this run belongs to'
    )
    
    start_time = models.DateTimeField(
        auto_now_add=True,
        help_text='When the bot run was started'
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the bot run was stopped'
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='starting',
        help_text='Current status of this bot run'
    )
    
    trades_executed = models.PositiveIntegerField(
        default=0,
        help_text='Number of trades executed during this run'
    )
    
    profit_loss = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        default=0.0,
        help_text='Profit/Loss for this run (in base currency)'
    )
    
    error_message = models.TextField(
        blank=True,
        help_text='Error message if the run failed'
    )
    
    logs = models.JSONField(
        default=list,
        blank=True,
        help_text='Execution logs and events (JSON array)'
    )
    
    # Additional fields for API functionality
    run_parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text='Parameters passed when starting this run'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Notes or comments about this run'
    )
    
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='Celery task ID for tracking async execution'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bot Run'
        verbose_name_plural = 'Bot Runs'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['bot', '-start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        duration = ""
        if self.end_time:
            duration = f" ({self.duration})"
        return f"{self.bot.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}{duration}"
    
    @property
    def duration(self):
        """Calculate the duration of the bot run"""
        if not self.end_time:
            from django.utils import timezone
            end = timezone.now()
        else:
            end = self.end_time
        
        delta = end - self.start_time
        
        # Format duration as human-readable string
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_duration_seconds(self):
        """Get duration in seconds as a float"""
        if not self.start_time:
            return 0.0
        
        end_time = self.end_time or timezone.now()
        duration = end_time - self.start_time
        return duration.total_seconds()
    
    @property
    def is_running(self):
        """Check if this run is currently active"""
        return self.status in ['starting', 'running', 'stopping']
    
    def stop_run(self, status='completed', error_message=''):
        """Stop the bot run with given status"""
        from django.utils import timezone
        
        self.end_time = timezone.now()
        self.status = status
        if error_message:
            self.error_message = error_message
        self.save()
        
        # Update bot status
        if status == 'completed':
            self.bot.status = 'inactive'
            self.bot.save()
    
    def add_log(self, message, level='info'):
        """Add a log entry to this run"""
        from django.utils import timezone
        
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'level': level,
            'message': message
        }
        
        if not self.logs:
            self.logs = []
        
        self.logs.append(log_entry)
        self.save(update_fields=['logs', 'updated_at'])
