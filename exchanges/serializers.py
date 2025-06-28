from rest_framework import serializers
from .models import Exchange, UserAPIKey


class ExchangeSerializer(serializers.ModelSerializer):
    """Serializer for Exchange model"""
    
    class Meta:
        model = Exchange
        fields = ['id', 'name']


class UserAPIKeyListSerializer(serializers.ModelSerializer):
    """Serializer for listing user API keys (without secrets)"""
    exchange_name = serializers.CharField(source='exchange.name', read_only=True)
    
    class Meta:
        model = UserAPIKey
        fields = ['id', 'name', 'exchange', 'exchange_name', 'api_key_public_part', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserAPIKeyCreateSerializer(serializers.Serializer):
    """Serializer for creating new API keys"""
    name = serializers.CharField(max_length=100, help_text="Name for this API key")
    exchange = serializers.PrimaryKeyRelatedField(
        queryset=Exchange.objects.all(),
        help_text="Exchange this API key belongs to"
    )
    api_key = serializers.CharField(max_length=500, help_text="Public API key")
    secret_key = serializers.CharField(
        max_length=500, 
        write_only=True,
        help_text="Secret key (will be encrypted)"
    )
    
    def validate_name(self, value):
        """Validate that the name is unique for this user and exchange"""
        user = self.context['request'].user
        exchange = self.initial_data.get('exchange')
        
        if exchange and UserAPIKey.objects.filter(
            user=user, 
            exchange_id=exchange, 
            name=value
        ).exists():
            raise serializers.ValidationError(
                "You already have an API key with this name for this exchange."
            )
        return value
