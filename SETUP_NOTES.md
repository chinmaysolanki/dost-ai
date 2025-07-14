# DOST Setup Notes

## Current Status ✅
- Basic FastAPI server running on http://localhost:8000
- Core functionality working (chat, tasks, users, websocket)
- Simplified version without AI/voice features

## To Complete Full Installation 🔧

### 1. Install Remaining Dependencies
```bash
# Audio processing (when network is stable)
pip install openai-whisper pydub numpy scipy librosa soundfile

# Database and auth
pip install alembic asyncpg redis python-jose[cryptography] passlib[bcrypt]

# Background tasks and calendar
pip install celery[redis] apscheduler google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Environment Configuration
Create a `.env` file with:
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///./dost.db

# Google Calendar (optional)
GOOGLE_CALENDAR_CREDENTIALS_FILE=path/to/credentials.json

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

### 3. Switch to Full Version
Replace `main_simple.py` with `main.py` when ready:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the Current Version 🧪

### Create a user:
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Name", "email": "your@email.com"}'
```

### Chat with DOST:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello DOST!", "user_id": "user_1"}'
```

### Create a task:
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "My first task", "user_id": "user_1"}'
```

## Flutter App 📱
The Flutter app in `flutter_app/` is ready but will need the full backend for complete functionality.

## Troubleshooting 🔍
- If `python` command not found, use `python3` instead
- Check server status: `curl http://localhost:8000/status`
- View logs in the terminal where uvicorn is running
- API docs available at: http://localhost:8000/docs 