import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:wakelock/wakelock.dart';

import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'core/services/notification_service.dart';
import 'core/services/storage_service.dart';
import 'core/services/websocket_service.dart';
import 'core/services/api_service.dart';
import 'core/services/voice_service.dart';
import 'core/router/app_router.dart';
import 'core/providers/app_providers.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  
  // Initialize services
  await _initializeServices();
  
  // Request permissions
  await _requestPermissions();
  
  // Keep screen awake during voice interactions
  Wakelock.enable();
  
  runApp(
    ProviderScope(
      child: DOSTApp(),
    ),
  );
}

Future<void> _initializeServices() async {
  // Initialize storage service
  await StorageService.instance.initialize();
  
  // Initialize notification service
  await NotificationService.instance.initialize();
  
  // Initialize API service
  await ApiService.instance.initialize();
  
  // Initialize WebSocket service
  await WebSocketService.instance.initialize();
  
  // Initialize voice service
  await VoiceService.instance.initialize();
}

Future<void> _requestPermissions() async {
  // Request microphone permission
  await Permission.microphone.request();
  
  // Request notification permission
  await Permission.notification.request();
  
  // Request storage permission
  await Permission.storage.request();
}

class DOSTApp extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    final themeMode = ref.watch(themeModeProvider);
    
    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      
      // Theme configuration
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      
      // Router configuration
      routerConfig: router,
      
      // Builder for global overlays
      builder: (context, child) {
        return Scaffold(
          body: child,
          // Add global floating action button for quick voice access
          floatingActionButton: _buildGlobalVoiceButton(context, ref),
          floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
        );
      },
    );
  }
  
  Widget? _buildGlobalVoiceButton(BuildContext context, WidgetRef ref) {
    final currentRoute = ref.watch(currentRouteProvider);
    
    // Show voice button on main screens
    if (currentRoute == '/chat' || currentRoute == '/home') {
      return FloatingActionButton(
        onPressed: () => _handleVoiceButtonPress(context, ref),
        child: Consumer(
          builder: (context, ref, child) {
            final isListening = ref.watch(voiceServiceProvider).isListening;
            
            return AnimatedSwitcher(
              duration: Duration(milliseconds: 300),
              child: isListening
                  ? Icon(Icons.mic, key: ValueKey('listening'))
                  : Icon(Icons.mic_none, key: ValueKey('idle')),
            );
          },
        ),
        backgroundColor: Theme.of(context).primaryColor,
        heroTag: 'global_voice_button',
      );
    }
    
    return null;
  }
  
  void _handleVoiceButtonPress(BuildContext context, WidgetRef ref) {
    final voiceService = ref.read(voiceServiceProvider);
    
    if (voiceService.isListening) {
      voiceService.stopListening();
    } else {
      voiceService.startListening();
    }
  }
}

class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  
  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: Duration(seconds: 2),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
    
    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    
    _animationController.forward();
    
    // Navigate to home after animation
    Future.delayed(Duration(seconds: 3), () {
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    });
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).primaryColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Animated logo
            AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return Transform.scale(
                  scale: _scaleAnimation.value,
                  child: FadeTransition(
                    opacity: _fadeAnimation,
                    child: Column(
                      children: [
                        // App icon/logo
                        Container(
                          width: 120,
                          height: 120,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [
                                Colors.white.withOpacity(0.8),
                                Colors.white.withOpacity(0.6),
                              ],
                            ),
                          ),
                          child: Icon(
                            Icons.assistant,
                            size: 60,
                            color: Theme.of(context).primaryColor,
                          ),
                        ),
                        
                        SizedBox(height: 24),
                        
                        // App name
                        Text(
                          AppConstants.appName,
                          style: GoogleFonts.poppins(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        
                        SizedBox(height: 8),
                        
                        // App tagline
                        Text(
                          'Your AI Assistant',
                          style: GoogleFonts.poppins(
                            fontSize: 16,
                            color: Colors.white.withOpacity(0.8),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            
            SizedBox(height: 80),
            
            // Loading indicator
            FadeTransition(
              opacity: _fadeAnimation,
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 