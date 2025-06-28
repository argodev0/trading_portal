from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bots.models import Bot, BotRun
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'List all bots and their current status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Filter by username'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['active', 'inactive', 'paused', 'error'],
            help='Filter by bot status'
        )
        parser.add_argument(
            '--running',
            action='store_true',
            help='Show only currently running bots'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information'
        )
    
    def handle(self, *args, **options):
        username = options.get('user')
        status_filter = options.get('status')
        running_only = options.get('running', False)
        detailed = options.get('detailed', False)
        
        # Build queryset
        queryset = Bot.objects.select_related('user', 'exchange_key__exchange').prefetch_related('runs')
        
        if username:
            try:
                user = User.objects.get(username=username)
                queryset = queryset.filter(user=user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {username} not found'))
                return
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if running_only:
            queryset = queryset.filter(is_active=True)
        
        bots = queryset.order_by('user__username', 'name')
        
        if not bots.exists():
            self.stdout.write(self.style.WARNING('No bots found matching criteria'))
            return
        
        # Display bots
        self.stdout.write(self.style.SUCCESS(f'Found {bots.count()} bot(s):'))
        self.stdout.write('')
        
        for bot in bots:
            current_run = bot.get_current_run()
            total_runs = bot.get_total_runs()
            successful_runs = bot.get_successful_runs()
            
            # Status indicators
            status_color = {
                'active': self.style.SUCCESS,
                'inactive': self.style.WARNING,
                'paused': self.style.WARNING,
                'error': self.style.ERROR
            }.get(bot.status, self.style.WARNING)
            
            running_indicator = "🟢 RUNNING" if current_run else "⚪ STOPPED"
            
            self.stdout.write(f'📊 {bot.name} ({bot.user.username})')
            self.stdout.write(f'   Status: {status_color(bot.status.upper())} | {running_indicator}')
            self.stdout.write(f'   Strategy: {bot.get_strategy_display()} | Pair: {bot.pair} | Timeframe: {bot.get_timeframe_display()}')
            self.stdout.write(f'   Exchange: {bot.exchange_key.exchange.name}')
            
            if current_run:
                self.stdout.write(f'   🚀 Current Run: {current_run.duration} | Trades: {current_run.trades_executed} | P&L: {current_run.profit_loss:.8f}')
            
            if total_runs > 0:
                success_rate = (successful_runs / total_runs) * 100
                self.stdout.write(f'   📈 Performance: {total_runs} runs | {success_rate:.1f}% success rate')
            
            if detailed:
                self.stdout.write(f'   🔧 Config: Max trades/day: {bot.max_daily_trades} | Risk: {bot.risk_percentage}%')
                if bot.parameters:
                    self.stdout.write(f'   ⚙️ Parameters: {bot.parameters}')
                
                # Recent runs
                recent_runs = bot.runs.order_by('-start_time')[:3]
                if recent_runs:
                    self.stdout.write(f'   📋 Recent Runs:')
                    for run in recent_runs:
                        status_symbol = {
                            'completed': '✅',
                            'failed': '❌',
                            'cancelled': '🛑',
                            'running': '🟢'
                        }.get(run.status, '⚪')
                        
                        self.stdout.write(f'      {status_symbol} {run.start_time.strftime("%Y-%m-%d %H:%M")} | {run.duration} | {run.trades_executed} trades | {run.profit_loss:.8f}')
            
            self.stdout.write('')
        
        # Summary statistics
        total_bots = bots.count()
        active_bots = bots.filter(is_active=True).count()
        total_runs_all = sum(bot.get_total_runs() for bot in bots)
        
        self.stdout.write(self.style.SUCCESS('📊 Summary:'))
        self.stdout.write(f'   Total bots: {total_bots}')
        self.stdout.write(f'   Active bots: {active_bots}')
        self.stdout.write(f'   Total runs: {total_runs_all}')
        
        if active_bots > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🎮 Management commands:'))
            self.stdout.write('   python manage.py stop_bot <bot_id>  # Stop a specific bot')
            self.stdout.write('   python manage.py stop_bot --user <username> --all  # Stop all bots for user')
