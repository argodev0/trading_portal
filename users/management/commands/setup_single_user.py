import os
import base64
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exchanges.models import Exchange, UserAPIKey
from exchanges.services import KeyEncryptor

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up single user and API keys from environment variables'

    def handle(self, *args, **options):
        # Remove all existing users
        User.objects.all().delete()
        UserAPIKey.objects.all().delete()
        
        self.stdout.write('Removed all existing users and API keys')
        
        # Create the single user
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='admin',
            first_name='User',
            last_name='Account',
        )
        
        self.stdout.write(f'Created user: {user.username}')
        
        # Set up API keys from environment variables
        encryptor = KeyEncryptor()
        
        # Set up Binance API key
        binance_api_key = os.getenv('BINANCE_API_KEY')
        binance_api_secret = os.getenv('BINANCE_API_SECRET')
        
        if binance_api_key and binance_api_secret:
            binance_exchange, _ = Exchange.objects.get_or_create(name='binance')
            
            encrypted_credentials_b64, nonce_b64 = encryptor.encrypt(binance_api_key, binance_api_secret)
            
            UserAPIKey.objects.create(
                user=user,
                exchange=binance_exchange,
                name='Binance API',
                api_key_public_part=binance_api_key,
                encrypted_credentials=base64.b64decode(encrypted_credentials_b64),
                nonce=base64.b64decode(nonce_b64),
                is_active=True
            )
            self.stdout.write(f'Created Binance API key for {user.username}')

        # Set up KuCoin API key
        kucoin_api_key = os.getenv('KUCOIN_API_KEY')
        kucoin_api_secret = os.getenv('KUCOIN_API_SECRET')
        kucoin_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
        
        if kucoin_api_key and kucoin_api_secret and kucoin_passphrase:
            kucoin_exchange, _ = Exchange.objects.get_or_create(name='kucoin')
            
            # For KuCoin, store all three parameters
            credentials = f"{kucoin_api_key}:{kucoin_api_secret}:{kucoin_passphrase}"
            encrypted_credentials_b64, nonce_b64 = encryptor.encrypt(kucoin_api_key, credentials)
            
            UserAPIKey.objects.create(
                user=user,
                exchange=kucoin_exchange,
                name='KuCoin API',
                api_key_public_part=kucoin_api_key,
                encrypted_credentials=base64.b64decode(encrypted_credentials_b64),
                nonce=base64.b64decode(nonce_b64),
                is_active=True
            )
            self.stdout.write(f'Created KuCoin API key for {user.username}')

        self.stdout.write(self.style.SUCCESS('Single user setup completed!'))
        self.stdout.write(self.style.SUCCESS('Username: user'))
        self.stdout.write(self.style.SUCCESS('Password: admin'))
