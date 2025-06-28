"""
Test script for the KeyEncryptor service
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/root/trading_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_portal.settings')

# Set up Django
django.setup()

from exchanges.services import KeyEncryptor, APIKeyManager


def test_key_encryptor():
    """Test the KeyEncryptor class"""
    print("🔐 Testing KeyEncryptor Service")
    print("=" * 50)
    
    # Generate a master key for testing
    master_key = KeyEncryptor.generate_master_key()
    print(f"Generated master key: {master_key}")
    
    # Set the environment variable
    os.environ['MASTER_ENCRYPTION_KEY'] = master_key
    
    # Create encryptor instance
    encryptor = KeyEncryptor()
    print("✅ KeyEncryptor initialized successfully")
    
    # Test data
    test_api_key = "test_api_key_12345"
    test_secret_key = "test_secret_key_67890"
    
    print(f"\n📤 Encrypting credentials:")
    print(f"  API Key: {test_api_key}")
    print(f"  Secret Key: {test_secret_key}")
    
    # Encrypt
    try:
        encrypted_blob, nonce = encryptor.encrypt(test_api_key, test_secret_key)
        print(f"✅ Encryption successful!")
        print(f"  Encrypted blob length: {len(encrypted_blob)} bytes")
        print(f"  Nonce length: {len(nonce)} bytes")
        
        # Decrypt
        print(f"\n📥 Decrypting credentials:")
        decrypted_creds = encryptor.decrypt(encrypted_blob, nonce)
        print(f"✅ Decryption successful!")
        print(f"  Decrypted API Key: {decrypted_creds['api_key']}")
        print(f"  Decrypted Secret Key: {decrypted_creds['secret_key']}")
        
        # Verify data integrity
        if (decrypted_creds['api_key'] == test_api_key and 
            decrypted_creds['secret_key'] == test_secret_key):
            print("✅ Data integrity verified - encryption/decryption successful!")
        else:
            print("❌ Data integrity check failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🔧 Environment setup instructions:")
    print(f"Add this to your .env file:")
    print(f"MASTER_ENCRYPTION_KEY={master_key}")
    

def test_api_key_manager():
    """Test the APIKeyManager with database operations"""
    print(f"\n🗄️ Testing APIKeyManager with Database")
    print("=" * 50)
    
    try:
        from exchanges.models import Exchange, UserAPIKey
        from users.models import User
        
        # Get or create test data
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return
            
        exchange, created = Exchange.objects.get_or_create(name="Test Exchange")
        if created:
            print(f"✅ Created test exchange: {exchange.name}")
        
        # Test APIKeyManager
        manager = APIKeyManager()
        
        # Store credentials
        api_key_obj = manager.store_api_credentials(
            user=user,
            exchange=exchange,
            name="Test API Key",
            api_key="test_public_key_123",
            secret_key="test_secret_key_456"
        )
        print(f"✅ Stored API credentials for {user.username}")
        print(f"  API Key ID: {api_key_obj.id}")
        
        # Retrieve credentials
        retrieved_creds = manager.retrieve_api_credentials(api_key_obj)
        print(f"✅ Retrieved credentials:")
        print(f"  API Key: {retrieved_creds['api_key']}")
        print(f"  Secret Key: {retrieved_creds['secret_key']}")
        
        # Clean up test data
        api_key_obj.delete()
        if created:
            exchange.delete()
        print(f"✅ Test cleanup completed")
        
    except Exception as e:
        print(f"❌ Database test error: {e}")


if __name__ == "__main__":
    test_key_encryptor()
    test_api_key_manager()
