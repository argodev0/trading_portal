from django.db import models
from django.conf import settings
import uuid


class Exchange(models.Model):
    """Model representing a cryptocurrency exchange"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Name of the cryptocurrency exchange'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Exchange'
        verbose_name_plural = 'Exchanges'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserAPIKey(models.Model):
    """Model representing a user's API key for a specific exchange"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text='User who owns this API key'
    )
    
    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name='user_api_keys',
        help_text='Exchange this API key is for'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='User-friendly name for this API key'
    )
    
    api_key_public_part = models.CharField(
        max_length=255,
        help_text='Public part of the API key (non-sensitive)'
    )
    
    encrypted_credentials = models.BinaryField(
        help_text='Encrypted private API credentials'
    )
    
    nonce = models.BinaryField(
        help_text='Cryptographic nonce for encryption/decryption'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this API key is currently active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User API Key'
        verbose_name_plural = 'User API Keys'
        unique_together = ['user', 'exchange', 'name']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exchange.name} - {self.name}"
