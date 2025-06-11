import 'package:flutter/foundation.dart';
import 'dart:io' as io;

class ApiConfig {
  // Your computer's IP address for mobile device testing
  static const String _computerIpAddress = '192.168.178.26';
  
  static String get baseUrl {
    if (kIsWeb) {
      // For web, use localhost
      return 'http://$_computerIpAddress:8000';
    } else if (io.Platform.isAndroid) {
      // For Android emulator, use 10.0.2.2
      // For physical device, use your computer's IP address
      return kDebugMode 
          ? 'http://10.0.2.2:8000'  // Emulator
          : 'http://$_computerIpAddress:8000';  // Physical device
    } else if (io.Platform.isIOS) {
      // For iOS simulator, use localhost
      // For physical device, use your computer's IP address  
      return kDebugMode
          ? 'http://localhost:8000'  // Simulator
          : 'http://$_computerIpAddress:8000';  // Physical device
    } else {
      // Default for other platforms
      return 'http://localhost:8000';
    }
  }
  
  // You can uncomment and use this for physical devices
  // Replace 192.168.1.100 with your computer's actual IP address
  // static const String _physicalDeviceUrl = 'http://192.168.1.100:8000';
  
  static String get analyzeEndpoint => '$baseUrl/analyze/';
}
