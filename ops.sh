#!/bin/bash
# Trading Portal - Operations Script
# Quick commands for managing the trading portal system

echo "🚀 Trading Portal Operations"
echo "=============================="

show_status() {
    echo "📊 Service Status:"
    systemctl is-active gunicorn.socket && echo "  ✅ Gunicorn Socket: Active" || echo "  ❌ Gunicorn Socket: Inactive"
    systemctl is-active gunicorn.service && echo "  ✅ Gunicorn Service: Active" || echo "  ❌ Gunicorn Service: Inactive"
    systemctl is-active nginx.service && echo "  ✅ NGINX: Active" || echo "  ❌ NGINX: Inactive"
    echo ""
}

restart_services() {
    echo "🔄 Restarting services..."
    sudo systemctl restart gunicorn.service
    sudo systemctl restart nginx.service
    echo "✅ Services restarted"
    echo ""
}

run_tests() {
    echo "🧪 Running tests..."
    cd /root/trading_portal
    python manage.py check
    echo ""
    echo "🔐 Testing encryption service..."
    python test_encryption.py
    echo ""
    echo "🔑 Testing API keys endpoints..."
    python test_api_keys.py
    echo ""
    echo "🤖 Testing bot models..."
    python test_bot_models.py
    echo ""
    echo "⚡ Testing Celery tasks..."
    python test_celery_tasks.py
    echo ""
    echo "🧠 Testing AI strategy generator..."
    python test_strategy_generator.py
    echo ""
}

show_logs() {
    echo "📋 Recent logs:"
    echo "--- Gunicorn ---"
    sudo journalctl -u gunicorn.service --no-pager -n 10
    echo ""
    echo "--- NGINX ---"
    sudo journalctl -u nginx.service --no-pager -n 10
    echo ""
}

generate_key() {
    echo "🔑 Generating new master encryption key..."
    cd /root/trading_portal
    python manage.py generate_master_key
    echo ""
}

start_celery() {
    echo "⚡ Starting Celery worker..."
    cd /root/trading_portal
    celery -A trading_portal worker --loglevel=info --detach
    echo "✅ Celery worker started in background"
    echo ""
}

stop_celery() {
    echo "⚡ Stopping Celery worker..."
    pkill -f "celery worker"
    echo "✅ Celery worker stopped"
    echo ""
}

list_bots() {
    echo "🤖 Listing all bots..."
    cd /root/trading_portal
    python manage.py list_bots --detailed
    echo ""
}

case "$1" in
    "status")
        show_status
        ;;
    "restart")
        restart_services
        show_status
        ;;
    "test")
        run_tests
        ;;
    "logs")
        show_logs
        ;;
    "key")
        generate_key
        ;;
    "celery-start")
        start_celery
        ;;
    "celery-stop")
        stop_celery
        ;;
    "bots")
        list_bots
        ;;
    "strategies")
        echo "🧠 Testing AI strategy generator..."
        cd /root/trading_portal
        python test_strategy_generator.py
        ;;
    "all")
        show_status
        run_tests
        ;;
    *)
        echo "Usage: $0 {status|restart|test|logs|key|celery-start|celery-stop|bots|strategies|all}"
        echo ""
        echo "Commands:"
        echo "  status       - Show service status"
        echo "  restart      - Restart all services"
        echo "  test         - Run Django checks and all tests"
        echo "  logs         - Show recent service logs"
        echo "  key          - Generate new master encryption key"
        echo "  celery-start - Start Celery worker"
        echo "  celery-stop  - Stop Celery worker"
        echo "  bots         - List all bots and their status"
        echo "  strategies   - Test AI strategy generator"
        echo "  all          - Show status and run tests"
        echo ""
        ;;
esac
