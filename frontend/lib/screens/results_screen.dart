import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import '../config/api_config.dart';
import 'dart:typed_data';
import '../widgets/connection_footer.dart';

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
        backgroundColor: Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Detected Cards',
                style: TextStyle(
                  color: Color(0xFF10B981),
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 20),
              if (_markedImageData != null)
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.memory(
                    base64Decode(_markedImageData!.split(',')[1]),
                    fit: BoxFit.contain,
                  ),
                ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(ctx),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.1),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(color: Colors.white.withOpacity(0.2)),
                    ),
                  ),
                  child: const Text('Close'),
                ),
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
        backgroundColor: Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text("Error", style: TextStyle(color: Colors.red)),
        content: Text(message, style: const TextStyle(color: Colors.white)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("OK", style: TextStyle(color: Color(0xFF10B981))),
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
        backgroundColor: Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Icon(Icons.psychology_rounded, color: Color(0xFF10B981), size: 28),
                  const SizedBox(width: 12),
                  const Text(
                    'AI Advice',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              
              // Recommendation
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Color(0xFF10B981).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Color(0xFF10B981).withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Recommendation',
                      style: TextStyle(
                        color: Color(0xFF10B981),
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
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
              
              if (advice.containsKey('win_probability')) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Win Probability',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      Text(
                        '${advice['win_probability']}%',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              
              if (advice.containsKey('explanation')) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Why',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        advice['explanation'],
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              
              const SizedBox(height: 24),
              
              SizedBox(
                height: 48,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(ctx),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFF10B981),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    'Got it!',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
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

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                name,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF10B981),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Color(0xFF10B981).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Score: $score',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: cards
                .map((card) => Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.2),
                        ),
                      ),
                      child: Text(
                        card,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ))
                .toList(),
          ),
        ],
      ),
    );
  }

  Shader linearTitleShader(Rect bounds) => const LinearGradient(
        colors: [Colors.greenAccent, Colors.cyanAccent],
      ).createShader(bounds);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF0F172A),
              Color(0xFF1E293B),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // App bar
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_rounded, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                    Expanded(
                      child: Text(
                        'Results',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    SizedBox(width: 48), // Balance the back button
                  ],
                ),
              ),
              
              // Content
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.all(24),
                  children: [
                    // Show cards
                    if (widget.isAdviceMode) ...[
                      buildPlayerBlock('Your Cards', widget.results['player1']),
                    ] else ...[
                      buildPlayerBlock('Dealer', widget.results['dealer']),
                      const SizedBox(height: 16),
                      buildPlayerBlock('Player 1', widget.results['player1']),
                      if (widget.results.containsKey('player2')) ...[
                        const SizedBox(height: 16),
                        buildPlayerBlock('Player 2', widget.results['player2']),
                      ],
                    ],
                    
                    const SizedBox(height: 32),
                    
                    // Action buttons
                    if (widget.originalImage != null)
                      _buildActionButton(
                        'Show Detected Cards',
                        Icons.visibility_rounded,
                        _showMarkedContours,
                        isLoading: _isLoadingMarkedImage,
                      ),
                    
                    if (widget.isAdviceMode) ...[
                      const SizedBox(height: 16),
                      _buildActionButton(
                        'Show AI Advice',
                        Icons.psychology_rounded,
                        _getAIAdvice,
                        isLoading: _isLoadingAdvice,
                        isPrimary: true,
                      ),
                    ],
                    
                    const SizedBox(height: 16),
                    _buildActionButton(
                      'Play Again',
                      Icons.refresh_rounded,
                      () => Navigator.popUntil(context, (route) => route.isFirst),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Connection Footer
                    const ConnectionFooter(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildActionButton(
    String label,
    IconData icon,
    VoidCallback onPressed, {
    bool isLoading = false,
    bool isPrimary = false,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: isPrimary 
            ? Color(0xFF10B981) 
            : Colors.white.withOpacity(0.1),
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: isPrimary 
              ? BorderSide.none 
              : BorderSide(color: Colors.white.withOpacity(0.2)),
          ),
          elevation: 0,
        ),
        child: isLoading
          ? SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                color: Colors.white,
                strokeWidth: 2,
              ),
            )
          : Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 20),
                const SizedBox(width: 12),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
      ),
    );
  }
}
