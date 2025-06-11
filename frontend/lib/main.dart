import 'package:flutter/material.dart';
import 'screens/welcome_screen.dart';

void main() {
  runApp(const BlackjackVisionApp());
}

class BlackjackVisionApp extends StatelessWidget {
  const BlackjackVisionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blackjack Vision',
      theme: ThemeData.dark(useMaterial3: true),
      home: const WelcomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
