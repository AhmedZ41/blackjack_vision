import 'package:flutter/material.dart';

class WaitingScreen extends StatelessWidget {
  const WaitingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Glowing circular indicator
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.greenAccent.withOpacity(0.6),
                    blurRadius: 20,
                    spreadRadius: 5,
                  ),
                ],
              ),
              child: const CircularProgressIndicator(
                color: Colors.greenAccent,
                strokeWidth: 6,
              ),
            ),
            const SizedBox(height: 30),

            // Static styled text
            const Text(
              'Analyzing your image...',
              style: TextStyle(
                fontSize: 18,
                color: Colors.greenAccent,
                fontFamily: 'Courier', // Optional: retro-style font
                letterSpacing: 1.2,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
