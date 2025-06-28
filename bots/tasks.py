from celery import shared_task
from celery.exceptions import Retry
from django.utils import timezone
from django.conf import settings
import time
import logging
import random
import traceback
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple

from .models import Bot, BotRun

# Configure logging
logger = logging.getLogger(__name__)


class BotExecutionError(Exception):
    """Custom exception for bot execution errors"""
    pass


class MarketDataError(Exception):
    """Custom exception for market data errors"""
    pass


def fetch_market_data(bot: Bot) -> Dict[str, Any]:
    """
    Fetch latest market data for the bot's trading pair
    
    Args:
        bot: Bot instance with configuration
        
    Returns:
        Dict containing market data
        
    Raises:
        MarketDataError: If data fetching fails
    """
    try:
        # Simulate API call to exchange
        # In production, this would call the actual exchange API
        # using the bot's exchange_key credentials
        
        base_price = 45000.0  # Simulate BTC price
        
        # Simulate price movement
        price_change = random.uniform(-0.05, 0.05)  # ±5% movement
        current_price = base_price * (1 + price_change)
        
        # Simulate market data
        market_data = {
            'symbol': bot.pair,
            'price': current_price,
            'volume': random.uniform(100, 1000),
            'high_24h': current_price * 1.02,
            'low_24h': current_price * 0.98,
            'change_24h': price_change,
            'timestamp': timezone.now().isoformat(),
            'bid': current_price * 0.999,
            'ask': current_price * 1.001,
            'spread': current_price * 0.002
        }
        
        logger.info(f"Fetched market data for {bot.pair}: price={current_price:.2f}")
        return market_data
        
    except Exception as e:
        error_msg = f"Failed to fetch market data for {bot.pair}: {str(e)}"
        logger.error(error_msg)
        raise MarketDataError(error_msg)


def apply_strategy_logic(bot: Bot, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Apply the bot's strategy logic to determine if a trade signal is generated
    
    Args:
        bot: Bot instance with strategy configuration
        market_data: Latest market data
        
    Returns:
        Trade signal dict if signal generated, None otherwise
    """
    try:
        strategy = bot.strategy
        parameters = bot.parameters
        current_price = market_data['price']
        
        logger.info(f"Applying {strategy} strategy for {bot.name}")
        
        # Strategy implementations
        if strategy == 'grid':
            return apply_grid_strategy(bot, market_data, parameters)
        elif strategy == 'dca':
            return apply_dca_strategy(bot, market_data, parameters)
        elif strategy == 'scalping':
            return apply_scalping_strategy(bot, market_data, parameters)
        elif strategy == 'momentum':
            return apply_momentum_strategy(bot, market_data, parameters)
        elif strategy == 'mean_reversion':
            return apply_mean_reversion_strategy(bot, market_data, parameters)
        elif strategy == 'arbitrage':
            return apply_arbitrage_strategy(bot, market_data, parameters)
        else:
            logger.warning(f"Unknown strategy: {strategy}")
            return None
            
    except Exception as e:
        logger.error(f"Strategy logic error for {bot.name}: {str(e)}")
        return None


def apply_grid_strategy(bot: Bot, market_data: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Grid trading strategy implementation"""
    current_price = market_data['price']
    grid_size = parameters.get('grid_size', 10)
    price_range = parameters.get('price_range', {})
    
    min_price = price_range.get('min', current_price * 0.9)
    max_price = price_range.get('max', current_price * 1.1)
    
    # Simple grid logic - randomly generate signals for demo
    if random.random() < 0.1:  # 10% chance of signal
        action = 'buy' if current_price < (min_price + max_price) / 2 else 'sell'
        quantity = parameters.get('order_amount', 50.0) / current_price
        
        return {
            'action': action,
            'quantity': quantity,
            'price': current_price,
            'strategy': 'grid',
            'confidence': random.uniform(0.6, 0.9)
        }
    return None


def apply_dca_strategy(bot: Bot, market_data: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Dollar Cost Averaging strategy implementation"""
    # Simulate DCA logic - buy at regular intervals
    if random.random() < 0.05:  # 5% chance of DCA signal
        current_price = market_data['price']
        dca_amount = parameters.get('dca_amount', 100.0)
        
        return {
            'action': 'buy',
            'quantity': dca_amount / current_price,
            'price': current_price,
            'strategy': 'dca',
            'confidence': 0.8
        }
    return None


def apply_scalping_strategy(bot: Bot, market_data: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Scalping strategy implementation"""
    # Simulate scalping logic based on spread
    spread_threshold = parameters.get('spread_threshold', 0.001)
    current_spread = market_data.get('spread', 0)
    
    if current_spread > spread_threshold and random.random() < 0.15:
        current_price = market_data['price']
        action = random.choice(['buy', 'sell'])
        
        return {
            'action': action,
            'quantity': parameters.get('scalp_size', 0.01),
            'price': current_price,
            'strategy': 'scalping',
            'confidence': random.uniform(0.5, 0.7)
        }
    return None


def apply_momentum_strategy(bot: Bot, market_data: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Momentum trading strategy implementation"""
    change_24h = market_data.get('change_24h', 0)
    momentum_threshold = parameters.get('momentum_threshold', 0.02)
    
    if abs(change_24h) > momentum_threshold and random.random() < 0.08:
        current_price = market_data['price']
        action = 'buy' if change_24h > 0 else 'sell'
        
        return {
            'action': action,
            'quantity': parameters.get('position_size', 0.1),
            'price': current_price,
            'strategy': 'momentum',
            'confidence': min(0.9, abs(change_24h) * 10)
        }
    return None


def apply_mean_reversion_strategy(bot: Bot, market_data: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Mean reversion strategy implementation"""
    current_price = market_data['price']
    high_24h = market_data.get('high_24h', current_price)
    low_24h = market_data.get('low_24h', current_price)
    
    # Simple mean reversion logic
    mean_price = (high_24h + low_24h) / 2
    deviation_threshold = parameters.get('deviation_threshold', 0.02)
    
    deviation = abs(current_price - mean_price) / mean_price
    
    if deviation > deviation_threshold and random.random() < 0.06:
        action = 'buy' if current_price < mean_price else 'sell'
        
        return {
            'action': action,
            'quantity': parameters.get('reversion_size', 0.05),
            'price': current_price,
            'strategy': 'mean_reversion',
            'confidence': min(0.8, deviation * 5)
        }
    return None


def apply_arbitrage_strategy(bot: Bot, market_data: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Arbitrage strategy implementation"""
    # Simulate arbitrage opportunities
    if random.random() < 0.02:  # 2% chance of arbitrage opportunity
        current_price = market_data['price']
        
        return {
            'action': 'arbitrage',
            'quantity': parameters.get('arb_size', 0.1),
            'price': current_price,
            'strategy': 'arbitrage',
            'confidence': random.uniform(0.7, 0.95)
        }
    return None


def execute_trade(bot: Bot, signal: Dict[str, Any], run: BotRun) -> bool:
    """
    Execute a trade based on the generated signal
    
    Args:
        bot: Bot instance
        signal: Trade signal dictionary
        run: Current bot run instance
        
    Returns:
        bool: True if trade executed successfully, False otherwise
    """
    try:
        # This is a placeholder function for trade execution
        # In production, this would:
        # 1. Use the bot's exchange_key to authenticate with the exchange
        # 2. Place the actual order via exchange API
        # 3. Handle order confirmation and error cases
        # 4. Update portfolio/balance information
        
        action = signal['action']
        quantity = signal['quantity']
        price = signal['price']
        confidence = signal.get('confidence', 0.5)
        
        # Simulate trade execution delay
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate trade success/failure (95% success rate)
        trade_successful = random.random() < 0.95
        
        if trade_successful:
            # Simulate trade results
            executed_price = price * random.uniform(0.999, 1.001)  # Small slippage
            fee = executed_price * quantity * 0.001  # 0.1% fee
            net_amount = (executed_price * quantity) - fee
            
            # Update run statistics
            run.trades_executed += 1
            
            # Simple P&L calculation (very basic simulation)
            if action == 'sell':
                run.profit_loss += Decimal(str(net_amount * 0.01))  # Simulate small profit
            elif action == 'buy':
                run.profit_loss -= Decimal(str(fee))  # Account for fees
            
            run.save(update_fields=['trades_executed', 'profit_loss'])
            
            # Log the trade
            trade_log = f"Executed {action} {quantity:.6f} {bot.pair} at {executed_price:.2f} (confidence: {confidence:.2f})"
            run.add_log(trade_log, 'info')
            
            logger.info(f"Trade executed for {bot.name}: {trade_log}")
            return True
        else:
            error_msg = f"Trade execution failed for {action} {quantity:.6f} {bot.pair}"
            run.add_log(error_msg, 'error')
            logger.error(error_msg)
            return False
            
    except Exception as e:
        error_msg = f"Trade execution error: {str(e)}"
        run.add_log(error_msg, 'error')
        logger.error(f"Trade execution error for {bot.name}: {error_msg}")
        return False


@shared_task(bind=True, max_retries=3)
def run_bot_instance(self, run_id: str):
    """
    Celery task to run a bot instance in an infinite loop
    
    Args:
        run_id: UUID string of the BotRun instance
        
    The task will:
    1. Fetch latest market data for the bot's configuration
    2. Apply strategy logic to generate signals
    3. Execute trades if signals are generated
    4. Handle errors and logging
    5. Sleep for configured interval before next iteration
    """
    try:
        # Get the bot run instance
        try:
            run = BotRun.objects.select_related('bot', 'bot__user', 'bot__exchange_key').get(id=run_id)
            bot = run.bot
        except BotRun.DoesNotExist:
            logger.error(f"BotRun with ID {run_id} not found")
            return
        
        logger.info(f"Starting bot execution: {bot.name} (Run ID: {run_id})")
        
        # Update run status
        run.status = 'running'
        run.add_log(f"Bot execution started by Celery worker", 'info')
        run.save()
        
        # Update bot status
        bot.status = 'active'
        bot.is_active = True
        bot.save()
        
        execution_count = 0
        max_iterations = getattr(settings, 'BOT_MAX_RUNTIME', 24 * 60 * 60) // getattr(settings, 'BOT_EXECUTION_INTERVAL', 60)
        
        # Main execution loop
        while True:
            try:
                # Check if run is still active (could be stopped externally)
                run.refresh_from_db()
                if run.status not in ['running', 'starting']:
                    logger.info(f"Bot run {run_id} stopped externally with status: {run.status}")
                    break
                
                # Check maximum runtime
                execution_count += 1
                if execution_count > max_iterations:
                    run.add_log(f"Maximum runtime reached after {execution_count} iterations", 'warning')
                    break
                
                # Check daily trade limit
                if run.trades_executed >= bot.max_daily_trades:
                    run.add_log(f"Daily trade limit ({bot.max_daily_trades}) reached", 'warning')
                    break
                
                logger.debug(f"Bot {bot.name} - Iteration {execution_count}")
                
                # Step 1: Fetch latest market data
                try:
                    market_data = fetch_market_data(bot)
                    run.add_log(f"Market data fetched: {bot.pair} @ {market_data['price']:.2f}", 'debug')
                except MarketDataError as e:
                    run.add_log(f"Market data error: {str(e)}", 'error')
                    continue
                
                # Step 2: Apply strategy logic
                signal = apply_strategy_logic(bot, market_data)
                
                # Step 3: Execute trade if signal generated
                if signal:
                    run.add_log(f"Trade signal generated: {signal['action']} {signal['quantity']:.6f} @ {signal['price']:.2f}", 'info')
                    
                    try:
                        trade_executed = execute_trade(bot, signal, run)
                        if trade_executed:
                            logger.info(f"Trade executed successfully for {bot.name}")
                        else:
                            logger.warning(f"Trade execution failed for {bot.name}")
                    except Exception as e:
                        error_msg = f"Trade execution error: {str(e)}"
                        run.add_log(error_msg, 'error')
                        logger.error(f"Trade execution error for {bot.name}: {error_msg}")
                else:
                    run.add_log("No trade signal generated", 'debug')
                
                # Step 4: Sleep before next iteration
                sleep_interval = getattr(settings, 'BOT_EXECUTION_INTERVAL', 60)
                logger.debug(f"Bot {bot.name} sleeping for {sleep_interval} seconds")
                time.sleep(sleep_interval)
                
            except Exception as e:
                error_msg = f"Bot execution error: {str(e)}"
                run.add_log(error_msg, 'error')
                logger.error(f"Error in bot execution loop for {bot.name}: {error_msg}\n{traceback.format_exc()}")
                
                # Sleep before retrying
                time.sleep(30)
                continue
        
        # Bot execution completed normally
        run.stop_run(status='completed')
        logger.info(f"Bot execution completed: {bot.name} (Run ID: {run_id})")
        
    except Exception as e:
        logger.error(f"Critical error in run_bot_instance task: {str(e)}\n{traceback.format_exc()}")
        
        try:
            # Try to update run status if possible
            run = BotRun.objects.get(id=run_id)
            run.stop_run(status='failed', error_message=str(e))
        except:
            pass
        
        # Re-raise for Celery error handling
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task
def start_bot_execution(bot_id: str) -> str:
    """
    Start bot execution by creating a new BotRun and launching the execution task
    
    Args:
        bot_id: UUID string of the Bot instance
        
    Returns:
        str: BotRun ID if successful, None if failed
    """
    try:
        bot = Bot.objects.get(id=bot_id)
        
        # Check if bot is already running
        current_run = bot.get_current_run()
        if current_run:
            logger.warning(f"Bot {bot.name} is already running (Run ID: {current_run.id})")
            return str(current_run.id)
        
        # Create new bot run
        run = BotRun.objects.create(
            bot=bot,
            status='starting'
        )
        
        # Start the execution task
        run_bot_instance.delay(str(run.id))
        
        logger.info(f"Started bot execution for {bot.name} (Run ID: {run.id})")
        return str(run.id)
        
    except Bot.DoesNotExist:
        logger.error(f"Bot with ID {bot_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error starting bot execution: {str(e)}")
        return None


@shared_task
def stop_bot_execution(bot_id: str) -> bool:
    """
    Stop bot execution by updating the run status
    
    Args:
        bot_id: UUID string of the Bot instance
        
    Returns:
        bool: True if stopped successfully, False otherwise
    """
    try:
        bot = Bot.objects.get(id=bot_id)
        current_run = bot.get_current_run()
        
        if not current_run:
            logger.warning(f"Bot {bot.name} is not currently running")
            return False
        
        # Stop the run
        current_run.stop_run(status='cancelled')
        logger.info(f"Stopped bot execution for {bot.name} (Run ID: {current_run.id})")
        return True
        
    except Bot.DoesNotExist:
        logger.error(f"Bot with ID {bot_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error stopping bot execution: {str(e)}")
        return False
