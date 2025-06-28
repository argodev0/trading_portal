"""
Models for the strategies app.

This module defines the database models for storing AI-generated trading strategies.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.utils import timezone

User = get_user_model()


class GeneratedStrategy(models.Model):
    """
    Model for storing AI-generated trading strategies.
    """
    
    STRATEGY_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('error', 'Error'),
    ]
    
    STRATEGY_TYPE_CHOICES = [
        ('trend_following', 'Trend Following'),
        ('mean_reversion', 'Mean Reversion'),
        ('momentum', 'Momentum'),
        ('arbitrage', 'Arbitrage'),
        ('grid_trading', 'Grid Trading'),
        ('scalping', 'Scalping'),
        ('swing_trading', 'Swing Trading'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the generated strategy"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generated_strategies',
        help_text="User who generated this strategy"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Human-readable name for the strategy"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of what the strategy does"
    )
    
    original_prompt = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="Original user prompt used to generate the strategy"
    )
    
    generated_code = models.TextField(
        help_text="AI-generated Python code for the strategy"
    )
    
    strategy_type = models.CharField(
        max_length=50,
        choices=STRATEGY_TYPE_CHOICES,
        default='custom',
        help_text="Type/category of trading strategy"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STRATEGY_STATUS_CHOICES,
        default='draft',
        help_text="Current status of the strategy"
    )
    
    validation_results = models.JSONField(
        null=True,
        blank=True,
        help_text="Results from code validation checks"
    )
    
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Strategy parameters and configuration"
    )
    
    performance_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Performance metrics from backtesting or live trading"
    )
    
    ai_model_version = models.CharField(
        max_length=50,
        default='gemini-1.5-pro',
        help_text="Version of AI model used for generation"
    )
    
    generation_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadata about the generation process"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the strategy was first generated"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the strategy was last modified"
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this strategy can be shared with other users"
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this strategy has been used"
    )
    
    class Meta:
        verbose_name = "Generated Strategy"
        verbose_name_plural = "Generated Strategies"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['strategy_type', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
    def save(self, *args, **kwargs):
        # Auto-generate name if not provided
        if not self.name:
            self.name = f"Strategy {self.created_at or timezone.now()}"
        super().save(*args, **kwargs)
    
    def increment_usage(self):
        """Increment the usage counter for this strategy."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def is_valid(self):
        """Check if the strategy has passed validation."""
        return self.status == 'validated'
    
    def is_ready_for_use(self):
        """Check if the strategy is ready to be used in trading."""
        return self.status in ['validated', 'active']


class StrategyGenerationLog(models.Model):
    """
    Model for logging strategy generation attempts and their results.
    """
    
    GENERATION_STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('partial', 'Partial Success'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='strategy_generation_logs'
    )
    
    strategy = models.ForeignKey(
        GeneratedStrategy,
        on_delete=models.CASCADE,
        related_name='generation_logs',
        null=True,
        blank=True,
        help_text="Associated strategy if generation was successful"
    )
    
    prompt = models.TextField(
        help_text="Original prompt used for generation"
    )
    
    status = models.CharField(
        max_length=20,
        choices=GENERATION_STATUS_CHOICES,
        help_text="Status of the generation attempt"
    )
    
    ai_response_raw = models.TextField(
        blank=True,
        help_text="Raw response from AI model"
    )
    
    extracted_code = models.TextField(
        blank=True,
        help_text="Code extracted from AI response"
    )
    
    error_message = models.TextField(
        blank=True,
        help_text="Error message if generation failed"
    )
    
    processing_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to generate the strategy"
    )
    
    ai_model_used = models.CharField(
        max_length=50,
        default='gemini-1.5-pro',
        help_text="AI model used for generation"
    )
    
    tokens_used = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of tokens consumed in generation"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = "Strategy Generation Log"
        verbose_name_plural = "Strategy Generation Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Generation {self.status} for {self.user.email} at {self.created_at}"
