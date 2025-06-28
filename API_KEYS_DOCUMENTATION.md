# API Keys Endpoint Documentation

## Overview
The `/api/accounts/keys/` endpoint provides secure management of encrypted API keys for cryptocurrency exchanges using Django REST Framework.

## Authentication
All endpoints require JWT authentication. Include the Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

Get access tokens from `/api/auth/token/` with username/password.

## Endpoints

### 1. List User API Keys
**GET** `/api/accounts/keys/`

Lists all API keys for the authenticated user (secrets are never returned).

**Response Example:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": "d0ecfcb2-bcb6-4ae2-899f-90fcadf2d482",
      "name": "My Binance Key",
      "exchange": "a8882e47-1bf2-4c5d-b5d4-9126f11e4831",
      "exchange_name": "Binance",
      "api_key_public_part": "BNBX1234567890ABCDEF",
      "created_at": "2025-06-28T00:18:06.840000Z",
      "updated_at": "2025-06-28T00:18:06.840040Z"
    }
  ]
}
```

### 2. Create New API Key
**POST** `/api/accounts/keys/`

Creates a new API key with encrypted credentials using AES-GCM encryption.

**Request Body:**
```json
{
  "name": "My Exchange API Key",
  "exchange": "exchange-uuid-here",
  "api_key": "public_api_key_string",
  "secret_key": "secret_key_string"
}
```

**Field Descriptions:**
- `name` (string, required): User-friendly name for the API key
- `exchange` (UUID, required): UUID of the exchange this key belongs to
- `api_key` (string, required): Public API key from the exchange
- `secret_key` (string, required): Secret key (will be encrypted before storage)

**Response Example (201 Created):**
```json
{
  "success": true,
  "message": "API key created successfully",
  "data": {
    "id": "d0ecfcb2-bcb6-4ae2-899f-90fcadf2d482",
    "name": "My Exchange API Key",
    "exchange": "a8882e47-1bf2-4c5d-b5d4-9126f11e4831",
    "exchange_name": "Binance",
    "api_key_public_part": "public_api_key_string",
    "created_at": "2025-06-28T00:18:06.840000Z",
    "updated_at": "2025-06-28T00:18:06.840040Z"
  }
}
```

**Validation Errors (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid input data",
  "details": {
    "name": ["You already have an API key with this name for this exchange."],
    "exchange": ["This field is required."]
  }
}
```

### 3. Get Specific API Key
**GET** `/api/accounts/keys/{id}/`

Retrieves details of a specific API key (secrets are never returned).

**Response Example:**
```json
{
  "success": true,
  "data": {
    "id": "d0ecfcb2-bcb6-4ae2-899f-90fcadf2d482",
    "name": "My Exchange API Key",
    "exchange": "a8882e47-1bf2-4c5d-b5d4-9126f11e4831",
    "exchange_name": "Binance",
    "api_key_public_part": "public_api_key_string",
    "created_at": "2025-06-28T00:18:06.840000Z",
    "updated_at": "2025-06-28T00:18:06.840040Z"
  }
}
```

### 4. Delete API Key
**DELETE** `/api/accounts/keys/{id}/`

Permanently deletes an API key and its encrypted credentials.

**Response Example:**
```json
{
  "success": true,
  "message": "API key \"My Exchange API Key\" deleted successfully"
}
```

## Security Features

### Encryption
- **Algorithm**: AES-GCM (Galois/Counter Mode)
- **Key Size**: 256-bit master key
- **Nonce**: Unique 96-bit nonce per encryption
- **Authentication**: Built-in authenticated encryption

### Data Protection
- Secret keys are encrypted before database storage
- Only public parts of API keys are stored in plaintext
- Master encryption key stored in environment variables
- No secrets are ever returned in API responses

### Access Control
- JWT-based authentication required
- Users can only access their own API keys
- Admin interface available for management

## Error Responses

### Authentication Required (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### API Key Not Found (404)
```json
{
  "success": false,
  "error": "API key not found"
}
```

### Internal Server Error (500)
```json
{
  "success": false,
  "error": "Encryption failed",
  "detail": "Decryption failed: Invalid tag"
}
```

## Usage Example

### Python with requests
```python
import requests

# Authenticate
auth_response = requests.post('http://localhost:8000/api/auth/token/', {
    'username': 'your_username',
    'password': 'your_password'
})
token = auth_response.json()['access']

# Create API key
headers = {'Authorization': f'Bearer {token}'}
api_key_data = {
    'name': 'My Binance Key',
    'exchange': 'exchange-uuid',
    'api_key': 'public_key',
    'secret_key': 'secret_key'
}

response = requests.post(
    'http://localhost:8000/api/accounts/keys/',
    json=api_key_data,
    headers=headers
)
```

### curl
```bash
# Get token
TOKEN=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' \
    http://localhost:8000/api/auth/token/ | jq -r '.access')

# Create API key
curl -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "My Exchange Key",
        "exchange": "exchange-uuid",
        "api_key": "public_key",
        "secret_key": "secret_key"
    }' \
    http://localhost:8000/api/accounts/keys/
```

## Database Schema

The encrypted credentials are stored using the following models:

- **Exchange**: Stores exchange information (name, etc.)
- **UserAPIKey**: Stores encrypted API credentials per user/exchange
  - `encrypted_credentials`: AES-GCM encrypted blob
  - `nonce`: Unique nonce for each encryption
  - `api_key_public_part`: Unencrypted public API key part

## Environment Setup

Set the master encryption key in your environment:
```bash
export MASTER_ENCRYPTION_KEY="your-32-byte-base64-key"
```

Generate a new key with:
```bash
python manage.py generate_master_key
```
