from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from bots.models import Bot
from bots.tasks import stop_bot_execution

User = get_user_model()


class Command(BaseCommand):
    help = 'Stop a bot execution'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'bot_id',
            type=str,
            help='Bot ID to stop'
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
        parser.add_argument(
            '--all',
            action='store_true',
            help='Stop all running bots for a user (requires --user)'
        )
    
    def handle(self, *args, **options):
        bot_id = options['bot_id']
        username = options.get('user')
        bot_name = options.get('name')
        stop_all = options.get('all', False)
        
        try:
            if stop_all and username:
                # Stop all bots for a user
                try:
                    user = User.objects.get(username=username)
                    running_bots = Bot.objects.filter(
                        user=user,
                        is_active=True
                    )
                    
                    if not running_bots.exists():
                        self.stdout.write(
                            self.style.WARNING(f'No running bots found for user {username}')
                        )
                        return
                    
                    stopped_count = 0
                    for bot in running_bots:
                        success = stop_bot_execution(str(bot.id))
                        if success:
                            stopped_count += 1
                            self.stdout.write(f'  ✅ Stopped: {bot.name}')
                        else:
                            self.stdout.write(f'  ❌ Failed to stop: {bot.name}')
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Stopped {stopped_count} bots for user {username}')
                    )
                    return
                    
                except User.DoesNotExist:
                    raise CommandError(f'User {username} not found')
            
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
            
            # Check if bot is running
            current_run = bot.get_current_run()
            if not current_run:
                self.stdout.write(
                    self.style.WARNING(f'Bot "{bot.name}" is not currently running')
                )
                return
            
            # Stop bot execution
            success = stop_bot_execution(bot_id)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully stopped bot "{bot.name}"')
                )
                self.stdout.write(f'Run statistics:')
                self.stdout.write(f'  Duration: {current_run.duration}')
                self.stdout.write(f'  Trades executed: {current_run.trades_executed}')
                self.stdout.write(f'  Profit/Loss: {current_run.profit_loss:.8f}')
            else:
                raise CommandError('Failed to stop bot execution')
                
        except Exception as e:
            raise CommandError(f'Error stopping bot: {e}')
