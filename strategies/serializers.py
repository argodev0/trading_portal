"""
Serializers for the strategies app.
"""

from rest_framework import serializers
from .models import GeneratedStrategy, StrategyGenerationLog


class GenerateStrategyRequestSerializer(serializers.Serializer):
    """Serializer for strategy generation requests."""
    
    prompt = serializers.CharField(
        min_length=10,
        max_length=5000,
        help_text="Description of the trading strategy you want to generate"
    )
    
    name = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Optional name for the strategy"
    )
    
    strategy_type = serializers.ChoiceField(
        choices=GeneratedStrategy.STRATEGY_TYPE_CHOICES,
        required=False,
        default='custom',
        help_text="Type of trading strategy"
    )
    
    validate_code = serializers.BooleanField(
        default=True,
        help_text="Whether to validate the generated code"
    )


class GeneratedStrategySerializer(serializers.ModelSerializer):
    """Serializer for GeneratedStrategy model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    is_ready_for_use = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = GeneratedStrategy
        fields = [
            'id', 'user_email', 'name', 'description', 'original_prompt',
            'generated_code', 'strategy_type', 'status', 'validation_results',
            'parameters', 'performance_metrics', 'ai_model_version',
            'created_at', 'updated_at', 'is_public', 'usage_count',
            'is_valid', 'is_ready_for_use'
        ]
        read_only_fields = [
            'id', 'user_email', 'generated_code', 'validation_results',
            'ai_model_version', 'created_at', 'updated_at', 'usage_count',
            'is_valid', 'is_ready_for_use'
        ]


class GeneratedStrategyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for strategy listings."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    code_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedStrategy
        fields = [
            'id', 'user_email', 'name', 'strategy_type', 'status',
            'created_at', 'usage_count', 'is_public', 'code_preview'
        ]
    
    def get_code_preview(self, obj):
        """Return a preview of the generated code."""
        if obj.generated_code:
            preview = obj.generated_code[:200]
            if len(obj.generated_code) > 200:
                preview += "..."
            return preview
        return None


class StrategyGenerationLogSerializer(serializers.ModelSerializer):
    """Serializer for StrategyGenerationLog model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    strategy_name = serializers.CharField(source='strategy.name', read_only=True)
    
    class Meta:
        model = StrategyGenerationLog
        fields = [
            'id', 'user_email', 'strategy_name', 'prompt', 'status',
            'error_message', 'processing_time_seconds', 'ai_model_used',
            'tokens_used', 'created_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'strategy_name', 'prompt', 'status',
            'error_message', 'processing_time_seconds', 'ai_model_used',
            'tokens_used', 'created_at'
        ]


class StrategyValidationSerializer(serializers.Serializer):
    """Serializer for strategy validation requests."""
    
    code = serializers.CharField(
        help_text="Python code to validate"
    )


class StrategyValidationResponseSerializer(serializers.Serializer):
    """Serializer for strategy validation responses."""
    
    valid = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.CharField())
    warnings = serializers.ListField(child=serializers.CharField())
    has_function = serializers.BooleanField()
    has_imports = serializers.BooleanField()
    trading_keywords = serializers.ListField(child=serializers.CharField())
    syntax_valid = serializers.BooleanField(required=False)
