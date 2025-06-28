#!/usr/bin/env python
"""
Test script for the API Keys endpoints
Tests both authentication and key management functionality
"""
import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append('/root/trading_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from exchanges.models import Exchange
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_jwt_token(user):
    """Get JWT token for a user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_api_keys_endpoints():
    """Test the API keys endpoints"""
    print("🔑 Testing API Keys Endpoints")
    print("=" * 50)
    
    # Ensure we have a test user and exchange
    user, created = User.objects.get_or_create(
        email='testuser@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'account_tier': 'Free'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Created test user: {user.email}")
    else:
        print(f"✅ Using existing test user: {user.email}")
    
    # Ensure we have a test exchange
    exchange, created = Exchange.objects.get_or_create(
        name='Test Exchange',
        defaults={'name': 'Test Exchange'}
    )
    if created:
        print(f"✅ Created test exchange: {exchange.name}")
    else:
        print(f"✅ Using existing test exchange: {exchange.name}")
    
    # Get JWT token
    token = get_jwt_token(user)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    base_url = 'http://localhost:8000'
    
    print("\n📋 Testing GET /api/accounts/keys/ (List API keys)")
    try:
        response = requests.get(f'{base_url}/api/accounts/keys/', headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {data.get('count', 0)} API keys")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure Django server is running")
        print("   Run: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n📝 Testing POST /api/accounts/keys/ (Create API key)")
    try:
        payload = {
            'name': 'Test API Key',
            'exchange': str(exchange.id),  # Convert UUID to string
            'api_key': 'test_public_key_123456',
            'secret_key': 'test_secret_key_abcdef'
        }
        
        response = requests.post(
            f'{base_url}/api/accounts/keys/', 
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Success: Created API key")
            print(f"Response: {json.dumps(data, indent=2)}")
            created_key_id = data['data']['id']
        else:
            print(f"❌ Error: {response.text}")
            created_key_id = None
    except Exception as e:
        print(f"❌ Error: {e}")
        created_key_id = None
    
    # Test GET specific key if we created one
    if created_key_id:
        print(f"\n🔍 Testing GET /api/accounts/keys/{created_key_id}/ (Get specific key)")
        try:
            response = requests.get(f'{base_url}/api/accounts/keys/{created_key_id}/', headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: Retrieved API key details")
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print(f"\n🗑️ Testing DELETE /api/accounts/keys/{created_key_id}/ (Delete key)")
        try:
            response = requests.delete(f'{base_url}/api/accounts/keys/{created_key_id}/', headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: Deleted API key")
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🔒 Testing authentication required")
    try:
        # Test without authentication
        response = requests.get(f'{base_url}/api/accounts/keys/')
        print(f"Status without auth: {response.status_code}")
        if response.status_code == 401:
            print("✅ Success: Authentication required (401 Unauthorized)")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ API Keys endpoint testing completed!")
    return True

if __name__ == '__main__':
    test_api_keys_endpoints()
