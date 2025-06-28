"""
Utility functions for the exchanges app
"""
import os
from cryptography.fernet import Fernet
from django.conf import settings


class APIKeyEncryption:
    """Utility class for encrypting/decrypting API credentials"""
    
    @staticmethod
    def generate_key():
        """Generate a new encryption key"""
        return Fernet.generate_key()
    
    @staticmethod
    def encrypt_credentials(credentials_dict, key=None):
        """
        Encrypt API credentials
        Args:
            credentials_dict: Dict containing API secret and other sensitive data
            key: Encryption key (if None, generates a new one)
        Returns:
            tuple: (encrypted_data, nonce/key)
        """
        if key is None:
            key = Fernet.generate_key()
        
        fernet = Fernet(key)
        import json
        credentials_json = json.dumps(credentials_dict)
        encrypted_data = fernet.encrypt(credentials_json.encode())
        
        return encrypted_data, key
    
    @staticmethod
    def decrypt_credentials(encrypted_data, key):
        """
        Decrypt API credentials
        Args:
            encrypted_data: Encrypted credentials
            key: Decryption key
        Returns:
            dict: Decrypted credentials
        """
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        import json
        return json.loads(decrypted_data.decode())


def create_sample_data():
    """Create sample exchanges and API keys for testing"""
    from .models import Exchange, UserAPIKey
    from users.models import User
    
    # Create sample exchanges
    exchanges_data = [
        'Binance',
        'Coinbase Pro', 
        'Kraken',
        'Bybit',
        'KuCoin'
    ]
    
    created_exchanges = []
    for exchange_name in exchanges_data:
        exchange, created = Exchange.objects.get_or_create(name=exchange_name)
        created_exchanges.append(exchange)
        if created:
            print(f"Created exchange: {exchange_name}")
    
    # Create sample API key for first user
    user = User.objects.first()
    if user and created_exchanges:
        # Sample credentials to encrypt
        sample_credentials = {
            'api_secret': 'sample_secret_key_12345',
            'passphrase': 'sample_passphrase'  # For exchanges that require it
        }
        
        # Encrypt the credentials
        encrypted_data, nonce = APIKeyEncryption.encrypt_credentials(sample_credentials)
        
        api_key, created = UserAPIKey.objects.get_or_create(
            user=user,
            exchange=created_exchanges[0],  # Binance
            name='Main Trading Key',
            defaults={
                'api_key_public_part': 'public_key_abc123def456',
                'encrypted_credentials': encrypted_data,
                'nonce': nonce,
            }
        )
        
        if created:
            print(f"Created API key: {api_key}")
    
    return {
        'exchanges': Exchange.objects.count(),
        'api_keys': UserAPIKey.objects.count()
    }
