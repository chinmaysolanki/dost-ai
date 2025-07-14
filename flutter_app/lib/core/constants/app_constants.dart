class AppConstants {
  // App Information
  static const String appName = 'DOST';
  static const String appDescription = 'Your AI Assistant';
  static const String appVersion = '1.0.0';
  
  // API Configuration
  static const String baseUrl = 'http://localhost:8000';
  static const String websocketUrl = 'ws://localhost:8000/ws';
  static const String apiVersion = '/api/v1';
  
  // Storage Keys
  static const String userIdKey = 'user_id';
  static const String userTokenKey = 'user_token';
  static const String userPreferencesKey = 'user_preferences';
  static const String conversationHistoryKey = 'conversation_history';
  static const String settingsKey = 'settings';
  static const String themeModeKey = 'theme_mode';
  static const String voiceSettingsKey = 'voice_settings';
  
  // Voice Configuration
  static const Duration maxRecordingDuration = Duration(minutes: 5);
  static const Duration minRecordingDuration = Duration(seconds: 1);
  static const double voiceActivationThreshold = 0.5;
  
  // UI Configuration
  static const double defaultPadding = 16.0;
  static const double defaultBorderRadius = 12.0;
  static const double defaultElevation = 2.0;
  
  // Animation Durations
  static const Duration shortAnimationDuration = Duration(milliseconds: 200);
  static const Duration mediumAnimationDuration = Duration(milliseconds: 400);
  static const Duration longAnimationDuration = Duration(milliseconds: 600);
  
  // Message Types
  static const String messageTypeText = 'text';
  static const String messageTypeVoice = 'voice';
  static const String messageTypeSystem = 'system';
  static const String messageTypeImage = 'image';
  
  // WebSocket Events
  static const String wsEventConnection = 'connection';
  static const String wsEventMessage = 'message';
  static const String wsEventTyping = 'typing';
  static const String wsEventVoiceData = 'voice_data';
  static const String wsEventDisconnection = 'disconnection';
  
  // Error Messages
  static const String errorNetworkConnection = 'Network connection error';
  static const String errorVoicePermission = 'Microphone permission required';
  static const String errorVoiceRecording = 'Voice recording failed';
  static const String errorMessageSend = 'Failed to send message';
  static const String errorApiCall = 'API call failed';
  
  // Success Messages
  static const String successMessageSent = 'Message sent successfully';
  static const String successVoiceRecorded = 'Voice recorded successfully';
  static const String successSettingsSaved = 'Settings saved successfully';
  
  // Features
  static const List<String> supportedVoiceLanguages = [
    'en-US',
    'en-GB',
    'es-ES',
    'fr-FR',
    'de-DE',
    'it-IT',
    'pt-BR',
    'ja-JP',
    'ko-KR',
    'zh-CN',
  ];
  
  static const List<String> availableVoices = [
    'alloy',
    'echo',
    'fable',
    'onyx',
    'nova',
    'shimmer',
  ];
  
  // Theme Colors
  static const Map<String, int> primaryColors = {
    'blue': 0xFF2196F3,
    'purple': 0xFF9C27B0,
    'green': 0xFF4CAF50,
    'orange': 0xFFFF9800,
    'red': 0xFFF44336,
    'teal': 0xFF009688,
  };
  
  // Notification IDs
  static const int notificationIdMessage = 1;
  static const int notificationIdReminder = 2;
  static const int notificationIdTask = 3;
  static const int notificationIdCalendar = 4;
  
  // File Upload
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> supportedImageTypes = [
    'jpg',
    'jpeg',
    'png',
    'gif',
    'webp',
  ];
  
  static const List<String> supportedAudioTypes = [
    'mp3',
    'wav',
    'aac',
    'm4a',
    'ogg',
  ];
  
  // Default Values
  static const String defaultUserId = '1';
  static const String defaultUserName = 'User';
  static const String defaultVoice = 'alloy';
  static const String defaultLanguage = 'en-US';
  static const double defaultVolume = 1.0;
  static const double defaultSpeechRate = 1.0;
  static const double defaultSpeechPitch = 1.0;
  
  // Timeouts
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration websocketTimeout = Duration(seconds: 5);
  static const Duration voiceTimeout = Duration(seconds: 10);
  
  // Retry Configuration
  static const int maxRetryAttempts = 3;
  static const Duration retryDelay = Duration(seconds: 1);
  
  // Cache Configuration
  static const Duration cacheExpiration = Duration(hours: 1);
  static const int maxCacheSize = 100;
  
  // Analytics Events
  static const String analyticsEventAppOpen = 'app_open';
  static const String analyticsEventMessageSent = 'message_sent';
  static const String analyticsEventVoiceUsed = 'voice_used';
  static const String analyticsEventTaskCreated = 'task_created';
  static const String analyticsEventCalendarViewed = 'calendar_viewed';
  
  // Feature Flags
  static const bool enableVoiceProcessing = true;
  static const bool enableNotifications = true;
  static const bool enableAnalytics = true;
  static const bool enableDebugMode = false;
  
  // Conversation Limits
  static const int maxConversationHistory = 1000;
  static const int maxMessageLength = 2000;
  static const int maxVoiceRecordingLength = 300; // 5 minutes in seconds
  
  // UI Breakpoints
  static const double mobileBreakpoint = 600.0;
  static const double tabletBreakpoint = 1024.0;
  static const double desktopBreakpoint = 1440.0;
  
  // Accessibility
  static const Duration accessibilityAnnouncementDelay = Duration(milliseconds: 500);
  static const double minimumTouchTarget = 48.0;
  
  // Performance
  static const int maxConcurrentRequests = 5;
  static const Duration debounceDelay = Duration(milliseconds: 300);
  
  // Validation
  static const int minPasswordLength = 8;
  static const int maxPasswordLength = 128;
  static const int maxUsernameLength = 50;
  static const int maxEmailLength = 255;
  
  // Help & Support
  static const String helpUrl = 'https://dost.ai/help';
  static const String supportEmail = 'support@dost.ai';
  static const String privacyPolicyUrl = 'https://dost.ai/privacy';
  static const String termsOfServiceUrl = 'https://dost.ai/terms';
  
  // Social Media
  static const String twitterUrl = 'https://twitter.com/dostai';
  static const String githubUrl = 'https://github.com/dostai';
  static const String websiteUrl = 'https://dost.ai';
  
  // Default Responses
  static const String defaultGreeting = 'Hello! I\'m DOST, your AI assistant. How can I help you today?';
  static const String defaultError = 'I apologize, but I encountered an error. Please try again.';
  static const String defaultOffline = 'I\'m currently offline. Please check your connection.';
  
  // Conversation Starters
  static const List<String> conversationStarters = [
    'What can you help me with today?',
    'Tell me about the weather',
    'Help me plan my day',
    'Create a reminder for me',
    'What\'s on my calendar?',
    'Tell me a joke',
    'Help me with a task',
    'What\'s new?',
  ];
  
  // Quick Actions
  static const List<Map<String, String>> quickActions = [
    {'title': 'Weather', 'action': 'weather', 'icon': 'weather'},
    {'title': 'Calendar', 'action': 'calendar', 'icon': 'calendar'},
    {'title': 'Tasks', 'action': 'tasks', 'icon': 'task'},
    {'title': 'Reminders', 'action': 'reminders', 'icon': 'reminder'},
    {'title': 'Notes', 'action': 'notes', 'icon': 'note'},
    {'title': 'Settings', 'action': 'settings', 'icon': 'settings'},
  ];
} 