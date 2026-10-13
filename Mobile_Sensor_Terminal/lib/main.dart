import 'dart:io' show Platform;

import 'package:flutter/material.dart';
import 'package:sensor_terminal/screens/connection_screen.dart';
import 'package:sensor_terminal/screens/splash_screen.dart';

/// Stores the app startup timestamp for use in the About screen.
DateTime? appStartupTime;

/// App version constant.
const String appVersion = '1.0.0-beta.1';

void _logStartup() {
  appStartupTime = DateTime.now();
  final os = Platform.operatingSystem;
  final osVersion = Platform.operatingSystemVersion;
  final timestamp = appStartupTime!.toIso8601String();
  // ignore: avoid_print
  print('GaiaCode Sensor Terminal v$appVersion starting on $os ($osVersion) at $timestamp');
}

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  _logStartup();
  runApp(const SensorTerminalApp());
}

class SensorTerminalApp extends StatelessWidget {
  const SensorTerminalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GaiaCode Sensor Terminal',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFF0EADB2),
          onPrimary: Colors.white,
          secondary: const Color(0xFF0EADB2),
          surface: const Color(0xFF0f172a),
          onSurface: Colors.white,
        ),
        scaffoldBackgroundColor: const Color(0xFF0f172a),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1e293b),
          foregroundColor: Colors.white,
          elevation: 0,
        ),
        cardTheme: const CardThemeData(
          color: Color(0xFF1e293b),
        ),
      ),
      home: const SplashScreen(),
    );
  }
}
