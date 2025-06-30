#!/bin/bash

# Test script for connection status endpoints (Development mode only)
# This script tests the exchange connection status API endpoints

echo "=== Exchange Connection Status Test ==="
echo "Note: This requires Django backend to be running on localhost:8000"
echo ""

# Check if Django is running
if ! curl -s http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "❌ Django backend is not running on localhost:8000"
    echo "Start Django with: python manage.py runserver 127.0.0.1:8000"
    exit 1
fi

echo "✅ Django backend is running"
echo ""

# Test Binance connection status
echo "Testing Binance connection status..."
curl -s -X GET "http://localhost:8000/api/exchanges/binance/status/" \
     -H "Content-Type: application/json" | jq . || echo "❌ Binance test failed"

echo ""

# Test KuCoin connection status  
echo "Testing KuCoin connection status..."
curl -s -X GET "http://localhost:8000/api/exchanges/kucoin/status/" \
     -H "Content-Type: application/json" | jq . || echo "❌ KuCoin test failed"

echo ""
echo "=== Test Complete ==="
echo "Check the results above for connection status."
echo "Note: You may need authentication tokens for full testing."
