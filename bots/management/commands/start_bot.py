from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from bots.models import Bot
from bots.tasks import start_bot_execution

User = get_user_model()


class Command(BaseCommand):
    help = 'Start a bot execution using Celery'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'bot_id',
            type=str,
            help='Bot ID to start'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username of bot owner (alternative to bot_id)'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Bot name (used with --user)'
        )
    
    def handle(self, *args, **options):
        bot_id = options['bot_id']
        username = options.get('user')
        bot_name = options.get('name')
        
        try:
            # Find bot by ID or by user/name combination
            if username and bot_name:
                try:
                    user = User.objects.get(username=username)
                    bot = Bot.objects.get(user=user, name=bot_name)
                    bot_id = str(bot.id)
                except (User.DoesNotExist, Bot.DoesNotExist) as e:
                    raise CommandError(f'Bot not found: {e}')
            else:
                try:
                    bot = Bot.objects.get(id=bot_id)
                except Bot.DoesNotExist:
                    raise CommandError(f'Bot with ID {bot_id} not found')
            
            # Check if bot is already running
            current_run = bot.get_current_run()
            if current_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'Bot "{bot.name}" is already running (Run ID: {current_run.id})'
                    )
                )
                return
            
            # Start bot execution
            run_id = start_bot_execution(bot_id)
            
            if run_id:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully started bot "{bot.name}" (Run ID: {run_id})'
                    )
                )
                self.stdout.write(f'Bot configuration:')
                self.stdout.write(f'  Strategy: {bot.get_strategy_display()}')
                self.stdout.write(f'  Pair: {bot.pair}')
                self.stdout.write(f'  Timeframe: {bot.get_timeframe_display()}')
                self.stdout.write(f'  Max daily trades: {bot.max_daily_trades}')
                self.stdout.write(f'  Risk percentage: {bot.risk_percentage}%')
            else:
                raise CommandError('Failed to start bot execution')
                
        except Exception as e:
            raise CommandError(f'Error starting bot: {e}')
