import 'package:flutter/material.dart';
import 'dart:convert';

class ResultsScreen extends StatelessWidget {
  final Map<String, dynamic> results;

  ResultsScreen({super.key, required String resultsJson})
      : results = jsonDecode(resultsJson);

  Widget buildPlayerBlock(String name, Map<String, dynamic> data) {
    final cards = List<String>.from(data['cards']);
    final score = data['score'];

    return Card(
      color: Colors.grey.shade900,
      margin: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.greenAccent.withOpacity(0.2)),
      ),
      elevation: 6,
      child: Padding(
        padding: const EdgeInsets.all(18.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              name,
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.greenAccent,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: cards
                  .map((card) => Chip(
                        label: Text(card,
                            style: const TextStyle(
                                fontSize: 16, color: Colors.white)),
                        backgroundColor: Colors.black,
                        shape: StadiumBorder(
                          side: BorderSide(
                            color: Colors.greenAccent.withOpacity(0.3),
                          ),
                        ),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 14),
            Text(
              'Total: $score',
              style: const TextStyle(
                fontSize: 18,
                color: Colors.white,
                fontFamily: 'Courier',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Shader linearTitleShader(Rect bounds) => const LinearGradient(
        colors: [Colors.greenAccent, Colors.cyanAccent],
      ).createShader(bounds);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: ShaderMask(
          shaderCallback: (bounds) => linearTitleShader(bounds),
          child: const Text(
            "Results",
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white, // Fallback color
              letterSpacing: 1.5,
            ),
          ),
        ),
        backgroundColor: Colors.grey.shade900,
        centerTitle: true,
        elevation: 4,
      ),
      body: ListView(
        padding: const EdgeInsets.only(top: 20, bottom: 40),
        children: [
          buildPlayerBlock('Dealer', results['dealer']),
          buildPlayerBlock('Player 1', results['player1']),
          if (results.containsKey('player2'))
            buildPlayerBlock('Player 2', results['player2']),
          const SizedBox(height: 30),
          Center(
            child: ElevatedButton(
              onPressed: () {
                Navigator.popUntil(context, (route) => route.isFirst);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.greenAccent.withOpacity(0.1),
                foregroundColor: Colors.greenAccent,
                padding:
                    const EdgeInsets.symmetric(horizontal: 36, vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: const BorderSide(color: Colors.greenAccent),
                ),
              ),
              child: const Text(
                'Play Again',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
