import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exchanges.models import Exchange, UserAPIKey
from exchanges.services import KeyEncryptor

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up API keys from environment variables'

    def handle(self, *args, **options):
        encryptor = KeyEncryptor()
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@trading.local',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.email}')

        # Set up Binance API key
        binance_api_key = os.getenv('BINANCE_API_KEY')
        binance_api_secret = os.getenv('BINANCE_API_SECRET')
        
        if binance_api_key and binance_api_secret:
            binance_exchange, _ = Exchange.objects.get_or_create(name='binance')
            
            # Delete existing keys to ensure we use latest from env
            UserAPIKey.objects.filter(
                user=admin_user,
                exchange=binance_exchange
            ).delete()
            
            encrypted_credentials, nonce = encryptor.encrypt(binance_api_key, binance_api_secret)
            
            UserAPIKey.objects.create(
                user=admin_user,
                exchange=binance_exchange,
                name='Environment Binance API',
                api_key_public_part=binance_api_key,
                encrypted_credentials=encrypted_credentials,
                nonce=nonce,
                is_active=True
            )
            self.stdout.write(f'Created Binance API key for {admin_user.email}')
        else:
            self.stdout.write('Binance API credentials not found in environment')

        # Set up KuCoin API key
        kucoin_api_key = os.getenv('KUCOIN_API_KEY')
        kucoin_api_secret = os.getenv('KUCOIN_API_SECRET')
        kucoin_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
        
        if kucoin_api_key and kucoin_api_secret and kucoin_passphrase:
            kucoin_exchange, _ = Exchange.objects.get_or_create(name='kucoin')
            
            # Delete existing keys to ensure we use latest from env
            UserAPIKey.objects.filter(
                user=admin_user,
                exchange=kucoin_exchange
            ).delete()
            
            # For KuCoin, we need to store the passphrase as well
            credentials = f"{kucoin_api_key}:{kucoin_api_secret}:{kucoin_passphrase}"
            encrypted_credentials, nonce = encryptor.encrypt(kucoin_api_key, credentials)
            
            UserAPIKey.objects.create(
                user=admin_user,
                exchange=kucoin_exchange,
                name='Environment KuCoin API',
                api_key_public_part=kucoin_api_key,
                encrypted_credentials=encrypted_credentials,
                nonce=nonce,
                is_active=True
            )
            self.stdout.write(f'Created KuCoin API key for {admin_user.email}')
        else:
            self.stdout.write('KuCoin API credentials not found in environment')

        self.stdout.write(self.style.SUCCESS('API key setup completed!'))
