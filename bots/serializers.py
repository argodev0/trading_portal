"""
Serializers for the bots app.

This module provides DRF serializers for bot-related models and API requests.
"""

from rest_framework import serializers
from .models import Bot, BotRun


class BotListSerializer(serializers.ModelSerializer):
    """Simplified serializer for bot listings."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    exchange_name = serializers.CharField(source='exchange_key.exchange.name', read_only=True)
    is_active = serializers.SerializerMethodField()
    current_run_id = serializers.SerializerMethodField()
    total_runs = serializers.SerializerMethodField()
    
    class Meta:
        model = Bot
        fields = [
            'id', 'user_email', 'name', 'strategy', 'pair', 'timeframe',
            'exchange_name', 'is_active', 'current_run_id', 'total_runs',
            'created_at', 'updated_at'
        ]
    
    def get_is_active(self, obj):
        """Check if the bot is currently active."""
        return obj.has_active_runs()
    
    def get_current_run_id(self, obj):
        """Get the current run ID if bot is active."""
        current_run = obj.get_current_run()
        return str(current_run.id) if current_run else None
    
    def get_total_runs(self, obj):
        """Get total number of runs for this bot."""
        return obj.get_total_runs()


class BotSerializer(serializers.ModelSerializer):
    """Complete serializer for Bot model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    exchange_name = serializers.CharField(source='exchange_key.exchange.name', read_only=True)
    exchange_key_name = serializers.CharField(source='exchange_key.name', read_only=True)
    is_active = serializers.SerializerMethodField()
    current_run = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Bot
        fields = [
            'id', 'user_email', 'name', 'strategy', 'pair',
            'timeframe', 'parameters', 'exchange_name', 'exchange_key_name',
            'is_active', 'current_run', 'statistics', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'exchange_name', 'exchange_key_name',
            'is_active', 'current_run', 'statistics', 'created_at', 'updated_at'
        ]
    
    def get_is_active(self, obj):
        """Check if the bot is currently active."""
        return obj.has_active_runs()
    
    def get_current_run(self, obj):
        """Get current run information if bot is active."""
        current_run = obj.get_current_run()
        if current_run:
            return BotRunSerializer(current_run).data
        return None
    
    def get_statistics(self, obj):
        """Get bot statistics."""
        return {
            'total_runs': obj.get_total_runs(),
            'successful_runs': obj.get_successful_runs(),
            'success_rate': obj.get_success_rate(),
            'last_run_at': obj.runs.order_by('-start_time').first().start_time if obj.runs.exists() else None
        }


class BotRunSerializer(serializers.ModelSerializer):
    """Serializer for BotRun model."""
    
    bot_name = serializers.CharField(source='bot.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    is_running = serializers.SerializerMethodField()
    
    class Meta:
        model = BotRun
        fields = [
            'id', 'bot_name', 'start_time', 'end_time', 'status',
            'trades_executed', 'profit_loss', 'error_message', 'notes',
            'run_parameters', 'celery_task_id', 'duration_seconds',
            'is_running', 'created_at'
        ]
        read_only_fields = [
            'id', 'bot_name', 'duration_seconds', 'is_running', 'created_at'
        ]
    
    def get_duration_seconds(self, obj):
        """Calculate run duration in seconds."""
        return obj.get_duration_seconds()
    
    def get_is_running(self, obj):
        """Check if the run is currently active."""
        return obj.is_running


class BotStartRequestSerializer(serializers.Serializer):
    """Serializer for bot start requests."""
    
    parameters = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Optional runtime parameters to override bot defaults"
    )
    
    notes = serializers.CharField(
        required=False,
        max_length=1000,
        help_text="Optional notes for this run"
    )


class BotStopRequestSerializer(serializers.Serializer):
    """Serializer for bot stop requests."""
    
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Optional reason for stopping the bot"
    )
    
    force = serializers.BooleanField(
        default=False,
        help_text="Force stop even if bot is in critical state"
    )


class BotCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new bots."""
    
    class Meta:
        model = Bot
        fields = [
            'name', 'strategy', 'pair', 'timeframe',
            'parameters', 'exchange_key'
        ]
    
    def validate_exchange_key(self, value):
        """Validate that the exchange key belongs to the current user."""
        if value.user != self.context['request'].user:
            raise serializers.ValidationError(
                "Exchange key does not belong to the current user"
            )
        return value
    
    def create(self, validated_data):
        """Create a new bot with the current user."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
