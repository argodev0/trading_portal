"""
Encryption services for the exchanges app
"""
import os
import json
import base64
import time
from typing import Dict, Tuple, Any
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class KeyEncryptor:
    """
    Encryption service for API keys using AES-GCM mode
    """
    
    def __init__(self):
        """Initialize the encryptor with master key from environment"""
        self.master_key = self._get_master_key()
    
    def _get_master_key(self) -> bytes:
        """
        Get the master encryption key from environment variable
        
        Returns:
            bytes: 32-byte master encryption key
            
        Raises:
            ImproperlyConfigured: If master key is not set or invalid
        """
        master_key_b64 = os.environ.get('MASTER_ENCRYPTION_KEY')
        
        if not master_key_b64:
            raise ImproperlyConfigured(
                "MASTER_ENCRYPTION_KEY environment variable is not set. "
                "Generate one with: python -c \"import base64; from Crypto.Random import get_random_bytes; "
                "print(base64.b64encode(get_random_bytes(32)).decode())\""
            )
        
        try:
            master_key = base64.b64decode(master_key_b64)
            if len(master_key) != 32:
                raise ValueError("Master key must be 32 bytes")
            return master_key
        except Exception as e:
            raise ImproperlyConfigured(
                f"Invalid MASTER_ENCRYPTION_KEY: {e}. "
                "Key must be a base64-encoded 32-byte value."
            )
    
    def encrypt(self, api_key: str, secret_key: str) -> Tuple[bytes, bytes]:
        """
        Encrypt API credentials using AES-GCM
        
        Args:
            api_key (str): The API key (public part)
            secret_key (str): The secret key (private part)
            
        Returns:
            Tuple[bytes, bytes]: (encrypted_blob, nonce)
                - encrypted_blob: Contains encrypted credentials + auth tag
                - nonce: Random nonce used for encryption
        """
        # Prepare credentials data
        credentials = {
            'api_key': api_key,
            'secret_key': secret_key,
            'timestamp': str(time.time())  # Add timestamp for additional verification
        }
        
        # Convert to JSON bytes
        credentials_json = json.dumps(credentials, sort_keys=True)
        credentials_bytes = credentials_json.encode('utf-8')
        
        # Generate random nonce (12 bytes is recommended for GCM)
        nonce = get_random_bytes(12)
        
        # Create cipher with master key and nonce
        cipher = AES.new(self.master_key, AES.MODE_GCM, nonce=nonce)
        
        # Encrypt and get authentication tag
        ciphertext, auth_tag = cipher.encrypt_and_digest(credentials_bytes)
        
        # Combine ciphertext and auth tag
        encrypted_blob = ciphertext + auth_tag
        
        return encrypted_blob, nonce
    
    def decrypt(self, encrypted_blob: bytes, nonce: bytes) -> Dict[str, str]:
        """
        Decrypt API credentials using AES-GCM
        
        Args:
            encrypted_blob (bytes): Encrypted credentials + auth tag
            nonce (bytes): Nonce used during encryption
            
        Returns:
            Dict[str, str]: Decrypted credentials containing 'api_key' and 'secret_key'
            
        Raises:
            ValueError: If decryption fails (wrong key, corrupted data, etc.)
        """
        try:
            # Split encrypted blob into ciphertext and auth tag
            # Auth tag is always 16 bytes for GCM
            if len(encrypted_blob) < 16:
                raise ValueError("Encrypted blob is too short")
            
            ciphertext = encrypted_blob[:-16]
            auth_tag = encrypted_blob[-16:]
            
            # Create cipher with master key and nonce
            cipher = AES.new(self.master_key, AES.MODE_GCM, nonce=nonce)
            
            # Decrypt and verify authentication tag
            decrypted_bytes = cipher.decrypt_and_verify(ciphertext, auth_tag)
            
            # Parse JSON
            credentials_json = decrypted_bytes.decode('utf-8')
            credentials = json.loads(credentials_json)
            
            # Validate required fields
            if 'api_key' not in credentials or 'secret_key' not in credentials:
                raise ValueError("Invalid credentials format")
            
            return {
                'api_key': credentials['api_key'],
                'secret_key': credentials['secret_key']
            }
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    @staticmethod
    def generate_master_key() -> str:
        """
        Generate a new base64-encoded master key
        
        Returns:
            str: Base64-encoded 32-byte master key
        """
        key_bytes = get_random_bytes(32)
        return base64.b64encode(key_bytes).decode('utf-8')


class APIKeyManager:
    """
    High-level manager for API key operations
    """
    
    def __init__(self):
        self.encryptor = KeyEncryptor()
    
    def store_api_credentials(self, user, exchange, name: str, api_key: str, secret_key: str) -> 'UserAPIKey':
        """
        Store encrypted API credentials for a user
        
        Args:
            user: User instance
            exchange: Exchange instance
            name (str): User-friendly name for the API key
            api_key (str): Public API key
            secret_key (str): Secret API key
            
        Returns:
            UserAPIKey: Created UserAPIKey instance
        """
        from .models import UserAPIKey
        
        # Encrypt the credentials
        encrypted_blob, nonce = self.encryptor.encrypt(api_key, secret_key)
        
        # Store in database
        user_api_key = UserAPIKey.objects.create(
            user=user,
            exchange=exchange,
            name=name,
            api_key_public_part=api_key,  # Store public part for reference
            encrypted_credentials=encrypted_blob,
            nonce=nonce
        )
        
        return user_api_key
    
    def retrieve_api_credentials(self, user_api_key: 'UserAPIKey') -> Dict[str, str]:
        """
        Retrieve and decrypt API credentials
        
        Args:
            user_api_key: UserAPIKey instance
            
        Returns:
            Dict[str, str]: Decrypted credentials
        """
        return self.encryptor.decrypt(
            user_api_key.encrypted_credentials,
            user_api_key.nonce
        )
    
    def update_api_credentials(self, user_api_key: 'UserAPIKey', api_key: str, secret_key: str) -> 'UserAPIKey':
        """
        Update existing API credentials with new encrypted values
        
        Args:
            user_api_key: UserAPIKey instance to update
            api_key (str): New public API key
            secret_key (str): New secret API key
            
        Returns:
            UserAPIKey: Updated UserAPIKey instance
        """
        # Encrypt new credentials
        encrypted_blob, nonce = self.encryptor.encrypt(api_key, secret_key)
        
        # Update the instance
        user_api_key.api_key_public_part = api_key
        user_api_key.encrypted_credentials = encrypted_blob
        user_api_key.nonce = nonce
        user_api_key.save()
        
        return user_api_key
