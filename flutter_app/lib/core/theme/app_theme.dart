import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Color Palette
  static const Color primaryColor = Color(0xFF2196F3);
  static const Color secondaryColor = Color(0xFF03DAC6);
  static const Color accentColor = Color(0xFFFF6B6B);
  static const Color backgroundColor = Color(0xFFF5F5F5);
  static const Color surfaceColor = Color(0xFFFFFFFF);
  static const Color errorColor = Color(0xFFF44336);
  static const Color successColor = Color(0xFF4CAF50);
  static const Color warningColor = Color(0xFFFF9800);
  static const Color infoColor = Color(0xFF2196F3);
  
  // Dark Mode Colors
  static const Color darkBackgroundColor = Color(0xFF121212);
  static const Color darkSurfaceColor = Color(0xFF1E1E1E);
  static const Color darkPrimaryColor = Color(0xFF64B5F6);
  static const Color darkSecondaryColor = Color(0xFF26C6DA);
  
  // Text Colors
  static const Color textPrimaryColor = Color(0xFF212121);
  static const Color textSecondaryColor = Color(0xFF757575);
  static const Color textPrimaryDarkColor = Color(0xFFFFFFFF);
  static const Color textSecondaryDarkColor = Color(0xFFB0B0B0);
  
  // Message Colors
  static const Color userMessageColor = Color(0xFF2196F3);
  static const Color aiMessageColor = Color(0xFFE3F2FD);
  static const Color systemMessageColor = Color(0xFFF5F5F5);
  
  // Voice Colors
  static const Color voiceActiveColor = Color(0xFF4CAF50);
  static const Color voiceInactiveColor = Color(0xFF9E9E9E);
  static const Color voiceRecordingColor = Color(0xFFF44336);
  
  // Common Text Styles
  static TextStyle get headingStyle => GoogleFonts.poppins(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: textPrimaryColor,
  );
  
  static TextStyle get subHeadingStyle => GoogleFonts.poppins(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: textPrimaryColor,
  );
  
  static TextStyle get bodyStyle => GoogleFonts.poppins(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: textPrimaryColor,
  );
  
  static TextStyle get captionStyle => GoogleFonts.poppins(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: textSecondaryColor,
  );
  
  static TextStyle get buttonStyle => GoogleFonts.poppins(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: Colors.white,
  );
  
  // Light Theme
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      
      // Color Scheme
      colorScheme: const ColorScheme.light(
        primary: primaryColor,
        secondary: secondaryColor,
        surface: surfaceColor,
        background: backgroundColor,
        error: errorColor,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: textPrimaryColor,
        onBackground: textPrimaryColor,
        onError: Colors.white,
      ),
      
      // App Bar Theme
      appBarTheme: AppBarTheme(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.poppins(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      
      // Card Theme
      cardTheme: CardTheme(
        color: surfaceColor,
        elevation: 2,
        shadowColor: Colors.black.withOpacity(0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      
      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceColor,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primaryColor, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: errorColor, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        hintStyle: GoogleFonts.poppins(
          color: textSecondaryColor,
          fontSize: 16,
        ),
      ),
      
      // Button Themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: buttonStyle,
        ),
      ),
      
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryColor,
          side: const BorderSide(color: primaryColor),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: buttonStyle.copyWith(color: primaryColor),
        ),
      ),
      
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: buttonStyle.copyWith(color: primaryColor),
        ),
      ),
      
      // Floating Action Button Theme
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 4,
        shape: CircleBorder(),
      ),
      
      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: surfaceColor,
        selectedItemColor: primaryColor,
        unselectedItemColor: textSecondaryColor,
        selectedLabelStyle: GoogleFonts.poppins(
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: GoogleFonts.poppins(
          fontSize: 12,
          fontWeight: FontWeight.normal,
        ),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      
      // Drawer Theme
      drawerTheme: DrawerThemeData(
        backgroundColor: surfaceColor,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.only(
            topRight: Radius.circular(16),
            bottomRight: Radius.circular(16),
          ),
        ),
      ),
      
      // List Tile Theme
      listTileTheme: ListTileThemeData(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        tileColor: surfaceColor,
        selectedTileColor: primaryColor.withOpacity(0.1),
        selectedColor: primaryColor,
        iconColor: textSecondaryColor,
        textColor: textPrimaryColor,
      ),
      
      // Divider Theme
      dividerTheme: DividerThemeData(
        color: Colors.grey.shade300,
        thickness: 1,
        space: 1,
      ),
      
      // Switch Theme
      switchTheme: SwitchThemeData(
        thumbColor: MaterialStateProperty.resolveWith<Color>(
          (states) => states.contains(MaterialState.selected) 
              ? primaryColor 
              : Colors.grey.shade400,
        ),
        trackColor: MaterialStateProperty.resolveWith<Color>(
          (states) => states.contains(MaterialState.selected) 
              ? primaryColor.withOpacity(0.3) 
              : Colors.grey.shade300,
        ),
      ),
      
      // Slider Theme
      sliderTheme: SliderThemeData(
        activeTrackColor: primaryColor,
        inactiveTrackColor: Colors.grey.shade300,
        thumbColor: primaryColor,
        overlayColor: primaryColor.withOpacity(0.1),
        valueIndicatorColor: primaryColor,
        valueIndicatorTextStyle: GoogleFonts.poppins(
          color: Colors.white,
          fontSize: 14,
        ),
      ),
      
      // Text Theme
      textTheme: GoogleFonts.poppinsTextTheme().copyWith(
        headlineLarge: headingStyle.copyWith(fontSize: 32),
        headlineMedium: headingStyle.copyWith(fontSize: 28),
        headlineSmall: headingStyle,
        titleLarge: subHeadingStyle.copyWith(fontSize: 22),
        titleMedium: subHeadingStyle.copyWith(fontSize: 20),
        titleSmall: subHeadingStyle,
        bodyLarge: bodyStyle.copyWith(fontSize: 18),
        bodyMedium: bodyStyle,
        bodySmall: bodyStyle.copyWith(fontSize: 14),
        labelLarge: buttonStyle.copyWith(fontSize: 16),
        labelMedium: buttonStyle.copyWith(fontSize: 14),
        labelSmall: captionStyle.copyWith(fontSize: 12),
      ),
    );
  }
  
  // Dark Theme
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      
      // Color Scheme
      colorScheme: const ColorScheme.dark(
        primary: darkPrimaryColor,
        secondary: darkSecondaryColor,
        surface: darkSurfaceColor,
        background: darkBackgroundColor,
        error: errorColor,
        onPrimary: Colors.black,
        onSecondary: Colors.black,
        onSurface: textPrimaryDarkColor,
        onBackground: textPrimaryDarkColor,
        onError: Colors.white,
      ),
      
      // App Bar Theme
      appBarTheme: AppBarTheme(
        backgroundColor: darkSurfaceColor,
        foregroundColor: textPrimaryDarkColor,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.poppins(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: textPrimaryDarkColor,
        ),
        iconTheme: const IconThemeData(color: textPrimaryDarkColor),
      ),
      
      // Card Theme
      cardTheme: CardTheme(
        color: darkSurfaceColor,
        elevation: 2,
        shadowColor: Colors.black.withOpacity(0.3),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      
      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: darkSurfaceColor,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.shade700),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: darkPrimaryColor, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: errorColor, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        hintStyle: GoogleFonts.poppins(
          color: textSecondaryDarkColor,
          fontSize: 16,
        ),
      ),
      
      // Button Themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: darkPrimaryColor,
          foregroundColor: Colors.black,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: buttonStyle.copyWith(color: Colors.black),
        ),
      ),
      
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: darkPrimaryColor,
          side: const BorderSide(color: darkPrimaryColor),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: buttonStyle.copyWith(color: darkPrimaryColor),
        ),
      ),
      
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: darkPrimaryColor,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: buttonStyle.copyWith(color: darkPrimaryColor),
        ),
      ),
      
      // Floating Action Button Theme
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: darkPrimaryColor,
        foregroundColor: Colors.black,
        elevation: 4,
        shape: CircleBorder(),
      ),
      
      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: darkSurfaceColor,
        selectedItemColor: darkPrimaryColor,
        unselectedItemColor: textSecondaryDarkColor,
        selectedLabelStyle: GoogleFonts.poppins(
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: GoogleFonts.poppins(
          fontSize: 12,
          fontWeight: FontWeight.normal,
        ),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      
      // Drawer Theme
      drawerTheme: DrawerThemeData(
        backgroundColor: darkSurfaceColor,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.only(
            topRight: Radius.circular(16),
            bottomRight: Radius.circular(16),
          ),
        ),
      ),
      
      // List Tile Theme
      listTileTheme: ListTileThemeData(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        tileColor: darkSurfaceColor,
        selectedTileColor: darkPrimaryColor.withOpacity(0.1),
        selectedColor: darkPrimaryColor,
        iconColor: textSecondaryDarkColor,
        textColor: textPrimaryDarkColor,
      ),
      
      // Divider Theme
      dividerTheme: DividerThemeData(
        color: Colors.grey.shade700,
        thickness: 1,
        space: 1,
      ),
      
      // Switch Theme
      switchTheme: SwitchThemeData(
        thumbColor: MaterialStateProperty.resolveWith<Color>(
          (states) => states.contains(MaterialState.selected) 
              ? darkPrimaryColor 
              : Colors.grey.shade600,
        ),
        trackColor: MaterialStateProperty.resolveWith<Color>(
          (states) => states.contains(MaterialState.selected) 
              ? darkPrimaryColor.withOpacity(0.3) 
              : Colors.grey.shade700,
        ),
      ),
      
      // Slider Theme
      sliderTheme: SliderThemeData(
        activeTrackColor: darkPrimaryColor,
        inactiveTrackColor: Colors.grey.shade700,
        thumbColor: darkPrimaryColor,
        overlayColor: darkPrimaryColor.withOpacity(0.1),
        valueIndicatorColor: darkPrimaryColor,
        valueIndicatorTextStyle: GoogleFonts.poppins(
          color: Colors.black,
          fontSize: 14,
        ),
      ),
      
      // Text Theme
      textTheme: GoogleFonts.poppinsTextTheme().copyWith(
        headlineLarge: headingStyle.copyWith(fontSize: 32, color: textPrimaryDarkColor),
        headlineMedium: headingStyle.copyWith(fontSize: 28, color: textPrimaryDarkColor),
        headlineSmall: headingStyle.copyWith(color: textPrimaryDarkColor),
        titleLarge: subHeadingStyle.copyWith(fontSize: 22, color: textPrimaryDarkColor),
        titleMedium: subHeadingStyle.copyWith(fontSize: 20, color: textPrimaryDarkColor),
        titleSmall: subHeadingStyle.copyWith(color: textPrimaryDarkColor),
        bodyLarge: bodyStyle.copyWith(fontSize: 18, color: textPrimaryDarkColor),
        bodyMedium: bodyStyle.copyWith(color: textPrimaryDarkColor),
        bodySmall: bodyStyle.copyWith(fontSize: 14, color: textPrimaryDarkColor),
        labelLarge: buttonStyle.copyWith(fontSize: 16, color: textPrimaryDarkColor),
        labelMedium: buttonStyle.copyWith(fontSize: 14, color: textPrimaryDarkColor),
        labelSmall: captionStyle.copyWith(fontSize: 12, color: textSecondaryDarkColor),
      ),
    );
  }
  
  // Custom Colors for Different Components
  static const Color chatBubbleUserColor = Color(0xFF2196F3);
  static const Color chatBubbleAIColor = Color(0xFFE8F5E8);
  static const Color chatBubbleUserDarkColor = Color(0xFF1976D2);
  static const Color chatBubbleAIDarkColor = Color(0xFF2E2E2E);
  
  static const Color voiceWaveColor = Color(0xFF4CAF50);
  static const Color voiceWaveDarkColor = Color(0xFF66BB6A);
  
  static const Color onlineStatusColor = Color(0xFF4CAF50);
  static const Color offlineStatusColor = Color(0xFF9E9E9E);
  static const Color typingStatusColor = Color(0xFFFF9800);
  
  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryColor, Color(0xFF1976D2)],
  );
  
  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accentColor, Color(0xFFE53935)],
  );
  
  static const LinearGradient voiceGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [voiceActiveColor, Color(0xFF388E3C)],
  );
} 