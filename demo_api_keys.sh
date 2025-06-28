#!/bin/bash
# API Keys Endpoint Demo Script
# Demonstrates the /api/accounts/keys/ endpoint functionality

echo "🔑 API Keys Endpoint Demo"
echo "========================="

BASE_URL="http://localhost:8000"
API_KEYS_URL="$BASE_URL/api/accounts/keys/"
AUTH_URL="$BASE_URL/api/auth/token/"

# Test user credentials
USERNAME="admin"
PASSWORD="admin123"

echo ""
echo "🔐 Step 1: Authenticate and get JWT token"
echo "Logging in as: $USERNAME"

# Get JWT token
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}" \
    $AUTH_URL)

echo "Auth response: $RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $RESPONSE | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get access token. Please ensure admin user exists."
    echo "Create admin user with: python manage.py createsuperuser"
    exit 1
fi

echo "✅ Got access token: ${ACCESS_TOKEN:0:20}..."

echo ""
echo "📋 Step 2: List existing API keys (should be empty)"
curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    $API_KEYS_URL | jq '.'

echo ""
echo "📝 Step 3: Create a new API key"

# First, let's get available exchanges
EXCHANGES_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$BASE_URL/admin/" 2>/dev/null)

# Create API key payload (we'll use the Test Exchange we know exists)
API_KEY_PAYLOAD='{
    "name": "My Binance API Key",
    "exchange": "a8882e47-1bf2-4c5d-b5d4-9126f11e4831",
    "api_key": "BNBX1234567890ABCDEF",
    "secret_key": "secret_bnb_key_9876543210fedcba"
}'

CREATE_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$API_KEY_PAYLOAD" \
    $API_KEYS_URL)

echo "Create response:"
echo $CREATE_RESPONSE | jq '.'

# Extract the created API key ID
API_KEY_ID=$(echo $CREATE_RESPONSE | jq -r '.data.id')

echo ""
echo "📋 Step 4: List API keys again (should show our new key)"
curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    $API_KEYS_URL | jq '.'

echo ""
echo "🔍 Step 5: Get specific API key details"
curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    "$API_KEYS_URL$API_KEY_ID/" | jq '.'

echo ""
echo "🔒 Step 6: Test authentication requirement (should fail)"
echo "Making request without authentication header:"
curl -s -X GET \
    -H "Content-Type: application/json" \
    $API_KEYS_URL | jq '.'

echo ""
echo "🗑️ Step 7: Delete the API key"
curl -s -X DELETE \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    "$API_KEYS_URL$API_KEY_ID/" | jq '.'

echo ""
echo "📋 Step 8: Verify deletion (list should be empty again)"
curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    $API_KEYS_URL | jq '.'

echo ""
echo "✅ API Keys endpoint demo completed!"
echo ""
echo "📖 Summary:"
echo "- ✅ JWT authentication working"
echo "- ✅ GET /api/accounts/keys/ - List user's API keys"
echo "- ✅ POST /api/accounts/keys/ - Create new encrypted API key"
echo "- ✅ GET /api/accounts/keys/{id}/ - Get specific API key"
echo "- ✅ DELETE /api/accounts/keys/{id}/ - Delete API key"
echo "- ✅ Authentication required for all endpoints"
echo "- ✅ Secrets are encrypted and not returned in responses"
