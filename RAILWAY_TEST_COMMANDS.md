# Railway Deployment Testing Commands

## Replace YOUR_RAILWAY_URL with your actual Railway URL

### 1. Health Check
```bash
curl https://YOUR_RAILWAY_URL/health
# Expected: {"status":"healthy","timestamp":"..."}
```

### 2. Welcome Message
```bash
curl https://YOUR_RAILWAY_URL/
# Expected: {"message":"Welcome to DOST - Your AI Friend! 🤖"}
```

### 3. System Status
```bash
curl https://YOUR_RAILWAY_URL/status
# Expected: Full system status with features and stats
```

### 4. Create Test User
```bash
curl -X POST https://YOUR_RAILWAY_URL/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
# Expected: {"user_id":"user_1","message":"User created successfully"}
```

### 5. Test Chat
```bash
curl -X POST https://YOUR_RAILWAY_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello DOST!", "user_id": "user_1"}'
# Expected: Chat response with simplified DOST message
```

### 6. API Documentation
Visit in browser: `https://YOUR_RAILWAY_URL/docs`
# Interactive Swagger UI with all endpoints

## Example with Real URL
If your URL is: `https://dost-ai-production.railway.app`

```bash
# Test health
curl https://dost-ai-production.railway.app/health

# Test chat
curl -X POST https://dost-ai-production.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "user_1"}'
``` 