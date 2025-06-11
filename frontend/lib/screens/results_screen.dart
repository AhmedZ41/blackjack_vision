import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io' as io;
import 'package:camera/camera.dart' as cam;
import 'waiting_screen.dart';
import 'results_screen.dart';
import 'package:http_parser/http_parser.dart';

class ResultsScreen extends StatelessWidget {
  final Map<String, dynamic> results;

  ResultsScreen({super.key, required String resultsJson})
      : results = jsonDecode(resultsJson);


  Widget buildPlayerBlock(String name, Map<String, dynamic> data) {
    final cards = List<String>.from(data['cards']);
    final score = data['score'];

    return Card(
      color: Colors.grey.shade900,
      margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 20),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              name,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.orangeAccent,
              ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: cards
                  .map((card) => Chip(
                        label: Text(card, style: const TextStyle(fontSize: 16)),
                        backgroundColor: Colors.black,
                        shape: StadiumBorder(
                            side: BorderSide(color: Colors.white24)),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 10),
            Text(
              'Total: $score',
              style: const TextStyle(fontSize: 18, color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("Results"),
        backgroundColor: Colors.grey.shade900,
      ),
      body: ListView(
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
              child: const Text('Play Again'),
            ),
          ),
        ],
      ),
    );
  }
}
