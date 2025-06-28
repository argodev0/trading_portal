#!/usr/bin/env python
"""
Simple test for the POST API endpoint
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/root/trading_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from exchanges.models import Exchange
from exchanges.services import APIKeyManager

User = get_user_model()

def test_api_key_creation():
    """Test API key creation directly"""
    print("🧪 Testing API Key Creation Directly")
    print("=" * 40)
    
    # Get or create test user
    try:
        user = User.objects.get(email='testuser@example.com')
        print(f"✅ Using existing user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User2',
            account_tier='Free'
        )
        print(f"✅ Created new user: {user.email}")
    
    # Get or create test exchange
    exchange, created = Exchange.objects.get_or_create(
        name='Test Exchange Direct'
    )
    
    try:
        # Test APIKeyManager directly
        api_key_manager = APIKeyManager()
        
        result = api_key_manager.store_api_credentials(
            user=user,
            exchange=exchange,
            name='Direct Test Key',
            api_key='test_public_123',
            secret_key='test_secret_456'
        )
        
        print(f"✅ Success: Created API key with ID: {result.id}")
        print(f"   Name: {result.name}")
        print(f"   Exchange: {result.exchange.name}")
        print(f"   Public Key Part: {result.api_key_public_part}")
        
        # Test retrieval
        retrieved = api_key_manager.retrieve_api_credentials(result)
        print(f"✅ Retrieved credentials:")
        print(f"   API Key: {retrieved['api_key']}")
        print(f"   Secret Key: {retrieved['secret_key']}")
        
        # Clean up
        result.delete()
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api_key_creation()
