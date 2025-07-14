# DOST - Your AI Assistant

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flutter-3.0+-blue.svg" alt="Flutter Version">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4-green.svg" alt="OpenAI GPT-4">
  <img src="https://img.shields.io/badge/FastAPI-0.104+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 🚀 Overview

DOST is a powerful AI assistant that listens to your voice, responds intelligently, manages your day, and grows smarter over time. Built with cutting-edge technology including Python FastAPI, Flutter mobile app, and OpenAI GPT-4, DOST truly feels like your best AI friend.

### ✨ Key Features

- **🗣️ Voice Interaction**: Natural voice conversations with OpenAI Whisper transcription and TTS
- **🧠 Intelligent Responses**: GPT-4 powered conversations with context awareness
- **📅 Calendar Management**: Smart scheduling with Google Calendar integration
- **✅ Task Management**: Intelligent task creation and organization
- **📱 Mobile App**: Beautiful Flutter app with voice interface
- **🔄 Real-time Communication**: WebSocket-based real-time updates
- **🎓 Adaptive Learning**: Gets smarter over time by learning your patterns
- **🌓 Modern UI**: Beautiful light/dark theme with smooth animations
- **📊 Analytics**: Insights into your productivity and usage patterns

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │   FastAPI API   │    │   OpenAI GPT-4  │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (AI Brain)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   PostgreSQL    │              │
         └──────────────┤   (Database)    │──────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │      Redis      │
                        │   (Caching)     │
                        └─────────────────┘
```

## 📋 Prerequisites

- Python 3.10+
- Flutter 3.0+
- Node.js 18+ (for development tools)
- PostgreSQL 13+ (optional, SQLite works too)
- Redis 6+ (optional, for caching)
- OpenAI API Key

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dost-ai-assistant.git
   cd dost-ai-assistant
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   **Required environment variables:**
   ```env
   # OpenAI Configuration (REQUIRED)
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4-turbo-preview
   
   # Database Configuration
   DATABASE_URL=sqlite:///./dost.db
   
   # Security
   SECRET_KEY=your-super-secret-key-change-this
   ```

4. **Initialize the database**
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

5. **Run the backend server**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Flutter App Setup

1. **Navigate to Flutter directory**
   ```bash
   cd flutter_app
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure app settings**
   - Update `lib/core/constants/app_constants.dart` with your backend URL
   - Ensure your backend is running on the configured URL

4. **Run the Flutter app**
   ```bash
   flutter run
   ```

## 🎯 Usage

### Basic Usage

1. **Start the backend server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Launch the Flutter app**
   ```bash
   cd flutter_app
   flutter run
   ```

3. **Start talking to DOST**
   - Tap the microphone button to start voice recording
   - Speak your message naturally
   - DOST will respond with both text and voice

### API Endpoints

#### Core Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /users/` - Create new user
- `GET /users/{user_id}` - Get user information

#### Voice & Chat

- `POST /voice/transcribe` - Transcribe voice message
- `POST /chat/message` - Send text message
- `GET /voice/audio/{conversation_id}` - Get audio response

#### Task Management

- `POST /tasks/` - Create new task
- `GET /tasks/` - Get user tasks
- `PUT /tasks/{task_id}` - Update task

#### Calendar

- `GET /calendar/today` - Get today's schedule
- `POST /calendar/events` - Create calendar event

#### Real-time Communication

- `WebSocket /ws/{user_id}` - WebSocket connection for real-time updates

### Voice Commands

DOST understands natural language commands:

- **"Create a task to buy groceries"**
- **"What's on my calendar today?"**
- **"Set a reminder for 2 PM"**
- **"Tell me about the weather"**
- **"Help me plan my day"**

## 🔧 Configuration

### Backend Configuration

Edit `.env` file:

```env
# Database - Choose one
DATABASE_URL=sqlite:///./dost.db  # SQLite (default)
# DATABASE_URL=postgresql://user:password@localhost/dost  # PostgreSQL

# OpenAI Settings
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
WHISPER_MODEL=whisper-1
TTS_VOICE=alloy  # Options: alloy, echo, fable, onyx, nova, shimmer

# Voice Processing
AUDIO_SAMPLE_RATE=16000
MAX_AUDIO_DURATION=300  # 5 minutes

# Google Calendar (Optional)
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=token.pickle
```

### Flutter App Configuration

Edit `flutter_app/lib/core/constants/app_constants.dart`:

```dart
// API Configuration
static const String baseUrl = 'http://your-backend-url:8000';
static const String websocketUrl = 'ws://your-backend-url:8000/ws';

// Voice Settings
static const String defaultVoice = 'alloy';
static const String defaultLanguage = 'en-US';
```

## 🧪 Development

### Backend Development

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests**
   ```bash
   pytest
   ```

3. **Code formatting**
   ```bash
   black .
   isort .
   ```

4. **Type checking**
   ```bash
   mypy .
   ```

### Flutter Development

1. **Code generation**
   ```bash
   flutter packages pub run build_runner build
   ```

2. **Testing**
   ```bash
   flutter test
   ```

3. **Code analysis**
   ```bash
   flutter analyze
   ```

## 📁 Project Structure

```
dost-ai-assistant/
├── app/                          # Backend application
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── database.py               # Database setup
│   ├── models.py                 # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   └── services/                 # Business logic services
│       ├── ai_brain.py           # GPT-4 integration
│       ├── voice_processor.py    # Voice processing
│       ├── calendar_manager.py   # Calendar management
│       ├── learning_system.py    # Adaptive learning
│       └── websocket_manager.py  # Real-time communication
├── flutter_app/                  # Flutter mobile application
│   ├── lib/
│   │   ├── main.dart            # App entry point
│   │   ├── core/                # Core functionality
│   │   │   ├── constants/       # App constants
│   │   │   ├── theme/          # App theming
│   │   │   └── services/       # Core services
│   │   ├── features/           # Feature modules
│   │   └── shared/             # Shared components
│   └── pubspec.yaml            # Flutter dependencies
├── requirements.txt             # Python dependencies
├── main.py                     # FastAPI application entry
└── README.md                   # This file
```

## 🎨 Features Deep Dive

### AI Brain (GPT-4 Integration)
- **Context Awareness**: Maintains conversation context across sessions
- **Intent Recognition**: Understands user intentions and extracts entities
- **Personality**: Warm, empathetic, and conversational
- **Action Processing**: Can create tasks, schedule events, and more

### Voice Processing
- **Transcription**: OpenAI Whisper for accurate speech-to-text
- **Text-to-Speech**: Natural-sounding voice responses
- **Audio Processing**: Noise reduction and quality optimization
- **Multiple Languages**: Support for 10+ languages

### Learning System
- **Pattern Recognition**: Learns from user behavior and preferences
- **Personalization**: Adapts responses based on user patterns
- **Insights Generation**: Provides analytics about user habits
- **Continuous Improvement**: Gets better over time

### Calendar Management
- **Google Calendar Integration**: Sync with your existing calendar
- **Smart Scheduling**: Suggests optimal meeting times
- **Event Creation**: Voice-activated event creation
- **Day Planning**: Intelligent day summary and planning

### Flutter Mobile App
- **Beautiful UI**: Modern design with smooth animations
- **Voice Interface**: One-tap voice recording
- **Real-time Updates**: WebSocket-powered live updates
- **Offline Support**: Works even without internet
- **Accessibility**: Full accessibility support

## 🚀 Deployment

### Backend Deployment

1. **Using Docker**
   ```bash
   docker build -t dost-backend .
   docker run -p 8000:8000 dost-backend
   ```

2. **Using Heroku**
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_key
   git push heroku main
   ```

3. **Using AWS/GCP**
   - Follow platform-specific deployment guides
   - Ensure environment variables are set
   - Configure database and Redis connections

### Flutter App Deployment

1. **Android APK**
   ```bash
   flutter build apk --release
   ```

2. **iOS App Store**
   ```bash
   flutter build ios --release
   ```

3. **Google Play Store**
   ```bash
   flutter build appbundle --release
   ```

## 🔒 Security

- **API Keys**: Never commit API keys to version control
- **Authentication**: Implement proper user authentication
- **Data Privacy**: User data is encrypted and secure
- **HTTPS**: Use HTTPS in production
- **Input Validation**: All inputs are validated and sanitized

## 📊 Monitoring

- **Health Checks**: Built-in health monitoring
- **Logging**: Comprehensive logging system
- **Performance Metrics**: Track response times and usage
- **Error Tracking**: Automatic error reporting
- **Analytics**: User behavior and app performance analytics

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: Check the [Wiki](https://github.com/yourusername/dost-ai-assistant/wiki)
- **Email**: support@dost.ai
- **Discord**: Join our [Discord community](https://discord.gg/dost)

## 🎉 Acknowledgments

- **OpenAI** for GPT-4 and Whisper APIs
- **Flutter Team** for the amazing framework
- **FastAPI** for the excellent web framework
- **Google** for Calendar API integration
- **Contributors** who make this project possible

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Integration with more calendar providers
- [ ] Advanced task management features
- [ ] Smart home integration
- [ ] Voice customization options
- [ ] Team collaboration features
- [ ] API marketplace for third-party integrations
- [ ] Desktop application
- [ ] Browser extension

---

<div align="center">
  <p>Built with ❤️ by the DOST Team</p>
  <p>
    <a href="https://dost.ai">Website</a> •
    <a href="https://twitter.com/dostai">Twitter</a> •
    <a href="https://github.com/dostai">GitHub</a>
  </p>
</div> 