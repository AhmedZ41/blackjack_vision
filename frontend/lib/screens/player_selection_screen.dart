import 'package:flutter/material.dart';
import 'camera_screen.dart';

class PlayerSelectionScreen extends StatelessWidget {
  const PlayerSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                '🧠 Choose Players 🎴',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  foreground: Paint()
                    ..shader = const LinearGradient(
                      colors: [Color(0xFF00FFD1), Color(0xFF3A3AFF)],
                    ).createShader(const Rect.fromLTWH(0, 0, 300, 70)),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Select the number of players below to start the card analysis.',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
              const Spacer(),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const CameraScreen(players: 1)),
                  );
                },
                style: ElevatedButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                  backgroundColor: const Color(0xFF00FFD1),
                  foregroundColor: Colors.black,
                  textStyle: const TextStyle(fontSize: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('1 Player'),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const CameraScreen(players: 2)),
                  );
                },
                style: ElevatedButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                  backgroundColor: const Color(0xFF00FFD1),
                  foregroundColor: Colors.black,
                  textStyle: const TextStyle(fontSize: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('2 Players'),
              ),
              const Spacer(),
            ],
          ),
        ),
      ),
    );
  }
}
