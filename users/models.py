import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with UUID primary key and account tier"""
    
    ACCOUNT_TIER_CHOICES = [
        ('Free', 'Free'),
        ('Premium', 'Premium'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    account_tier = models.CharField(
        max_length=10,
        choices=ACCOUNT_TIER_CHOICES,
        default='Free',
        help_text='User account subscription tier'
    )
    
    def __str__(self):
        return f"{self.username} ({self.account_tier})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
