import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import '../config/api_config.dart';
import 'dart:typed_data';

class ResultsScreen extends StatefulWidget {
  final Map<String, dynamic> results;
  final XFile? originalImage;
  final int players;
  final bool isAdviceMode;

  ResultsScreen({
    super.key, 
    required String resultsJson,
    this.originalImage,
    required this.players,
    this.isAdviceMode = false,
  }) : results = jsonDecode(resultsJson);

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  String? _markedImageData;
  bool _isLoadingMarkedImage = false;
  String? _aiAdvice;
  bool _isLoadingAdvice = false;

  Future<void> _showMarkedContours() async {
    if (widget.originalImage == null) {
      _showErrorDialog("No original image available");
      return;
    }

    setState(() {
      _isLoadingMarkedImage = true;
    });

    try {
      final uri = Uri.parse("${ApiConfig.baseUrl}/analyze/marked-contours/");
      final request = http.MultipartRequest('POST', uri)
        ..fields['players'] = widget.players.toString();

      // Add the image file
      final bytes = await widget.originalImage!.readAsBytes();
      final multipartFile = http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: widget.originalImage!.name,
      );
      request.files.add(multipartFile);

      final response = await request.send();

      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final responseData = jsonDecode(responseBody);
        
        if (responseData['success'] == true) {
          setState(() {
            _markedImageData = responseData['image'];
          });
          _showMarkedImageDialog();
        } else {
          _showErrorDialog("Failed to generate marked image");
        }
      } else {
        _showErrorDialog("Server error: ${response.statusCode}");
      }
    } catch (e) {
      _showErrorDialog("Failed to load marked image: $e");
    } finally {
      setState(() {
        _isLoadingMarkedImage = false;
      });
    }
  }

  void _showMarkedImageDialog() {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        backgroundColor: Colors.black,
        child: Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Detected Cards',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              if (_markedImageData != null)
                Image.memory(
                  base64Decode(_markedImageData!.split(',')[1]),
                  fit: BoxFit.contain,
                ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.pop(ctx),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.greenAccent.withOpacity(0.1),
                  foregroundColor: Colors.greenAccent,
                  side: const BorderSide(color: Colors.greenAccent),
                ),
                child: const Text('Close'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.grey.shade900,
        title: const Text("Error", style: TextStyle(color: Colors.red)),
        content: Text(message, style: const TextStyle(color: Colors.white)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("OK", style: TextStyle(color: Colors.greenAccent)),
          ),
        ],
      ),
    );
  }

  Future<void> _getAIAdvice() async {
    setState(() {
      _isLoadingAdvice = true;
    });

    try {
      // Extract advice from results if available
      if (widget.results.containsKey('advice')) {
        setState(() {
          _aiAdvice = widget.results['advice']['advice'];
        });
        _showAdviceDialog();
      } else {
        _showErrorDialog("No AI advice available");
      }
    } catch (e) {
      _showErrorDialog("Failed to get AI advice: $e");
    } finally {
      setState(() {
        _isLoadingAdvice = false;
      });
    }
  }

  void _showAdviceDialog() {
    if (_aiAdvice == null) return;

    final advice = widget.results['advice'];
    
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        backgroundColor: Colors.grey.shade900,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.psychology, color: Colors.orange, size: 28),
                  const SizedBox(width: 12),
                  const Text(
                    'AI Advice',
                    style: TextStyle(
                      color: Colors.orange,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              
              // Main recommendation
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orange.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Recommendation:',
                      style: TextStyle(
                        color: Colors.orange,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      advice['advice'] ?? 'No recommendation available',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Win probability
              if (advice.containsKey('win_probability'))
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.green.withOpacity(0.3)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Win Probability:',
                        style: TextStyle(
                          color: Colors.green,
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${advice['win_probability']}%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              
              const SizedBox(height: 16),
              
              // Explanation
              if (advice.containsKey('explanation'))
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade800.withOpacity(0.5),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Why:',
                        style: TextStyle(
                          color: Colors.grey,
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        advice['explanation'],
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              
              const SizedBox(height: 20),
              
              // Close button
              Center(
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(ctx),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange.withOpacity(0.1),
                    foregroundColor: Colors.orange,
                    side: const BorderSide(color: Colors.orange),
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                  ),
                  child: const Text('Got it!'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

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
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.greenAccent),
          onPressed: () => Navigator.pop(context),
        ),
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
          // In advice mode, only show player cards, no dealer
          if (widget.isAdviceMode) ...[
            buildPlayerBlock('Your Cards', widget.results['player1']),
          ] else ...[
            buildPlayerBlock('Dealer', widget.results['dealer']),
            buildPlayerBlock('Player 1', widget.results['player1']),
            if (widget.results.containsKey('player2'))
              buildPlayerBlock('Player 2', widget.results['player2']),
          ],
          const SizedBox(height: 30),
          // Show Detected Cards button (only if original image is available)
          if (widget.originalImage != null)
            Center(
              child: ElevatedButton(
                onPressed: _isLoadingMarkedImage ? null : _showMarkedContours,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent.withOpacity(0.1),
                  foregroundColor: Colors.blueAccent,
                  padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: const BorderSide(color: Colors.blueAccent),
                  ),
                ),
                child: _isLoadingMarkedImage
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.blueAccent,
                          strokeWidth: 2,
                        ),
                      )
                    : const Text(
                        'Show Detected Cards',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                      ),
              ),
            ),
          const SizedBox(height: 20),
          // AI Advice button (only in advice mode)
          if (widget.isAdviceMode)
            Center(
              child: ElevatedButton(
                onPressed: _isLoadingAdvice ? null : _getAIAdvice,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange.withOpacity(0.1),
                  foregroundColor: Colors.orange,
                  padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: const BorderSide(color: Colors.orange),
                  ),
                ),
                child: _isLoadingAdvice
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.orange,
                          strokeWidth: 2,
                        ),
                      )
                    : Row(
                        mainAxisSize: MainAxisSize.min,
                        children: const [
                          Icon(Icons.psychology, size: 20),
                          SizedBox(width: 8),
                          Text(
                            'Show AI\'s Advice',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
              ),
            ),
          const SizedBox(height: 20),
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
