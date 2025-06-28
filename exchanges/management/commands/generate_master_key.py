"""
Django management command to generate master encryption key
"""
from django.core.management.base import BaseCommand
from exchanges.services import KeyEncryptor


class Command(BaseCommand):
    """Generate a new master encryption key for API credential encryption"""
    
    help = 'Generate a new master encryption key for API credential encryption'
    
    def handle(self, *args, **options):
        """Generate and display a new master encryption key"""
        master_key = KeyEncryptor.generate_master_key()
        
        self.stdout.write(
            self.style.SUCCESS('🔐 Master Encryption Key Generated Successfully!')
        )
        self.stdout.write('')
        self.stdout.write('Add this to your environment variables:')
        self.stdout.write(f'MASTER_ENCRYPTION_KEY={master_key}')
        self.stdout.write('')
        self.stdout.write('For production deployment, add to your .env file:')
        self.stdout.write(f'echo "MASTER_ENCRYPTION_KEY={master_key}" >> .env')
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING(
                '⚠️  Keep this key secure! Loss of this key means loss of access to all encrypted API credentials.'
            )
        )
