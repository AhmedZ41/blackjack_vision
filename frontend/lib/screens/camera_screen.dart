import 'dart:io' as io;
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb, kDebugMode;
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart' as cam;
import 'waiting_screen.dart';
import 'results_screen.dart';
import 'dart:convert'; // At the top
import 'package:http_parser/http_parser.dart';
import '../config/api_config.dart';
import 'package:camera/camera.dart';
import 'package:flutter/services.dart'; // For web camera support
import '../widgets/connection_footer.dart';

const Color retroAccent = Color(0xFF00FFD1); 

class CameraScreen extends StatefulWidget {
  final int players;
  final bool isAdviceMode;
  
  const CameraScreen({
    super.key, 
    required this.players, 
    this.isAdviceMode = false
  });

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  // For mobile
  late cam.CameraController _controller;
  late Future<void> _initializeControllerFuture;

  // For web
  XFile? _webImage;

  @override
  void initState() {
    super.initState();
    if (!kIsWeb && (io.Platform.isAndroid || io.Platform.isIOS)) {
      _initMobileCamera();
    }
  }

  Future<void> _initMobileCamera() async {
    final cameras = await cam.availableCameras();
    final backCamera = cameras.firstWhere(
      (camera) => camera.lensDirection == cam.CameraLensDirection.back,
    );
    _controller = cam.CameraController(backCamera, cam.ResolutionPreset.medium);
    _initializeControllerFuture = _controller.initialize();
    if (mounted) setState(() {});
  }
Future<void> _testConnection() async {
    try {
      final response = await http.get(Uri.parse('${ApiConfig.baseUrl}/health'));
      if (response.statusCode == 200) {
        _showErrorDialog("Backend connection successful!\nURL: ${ApiConfig.baseUrl}");
      } else {
        _showErrorDialog("Backend responded with status: ${response.statusCode}");
      }
    } catch (e) {
      _showErrorDialog("Cannot connect to backend\nURL: ${ApiConfig.baseUrl}\nError: $e");
    }
  }


Future<void> _uploadImage(XFile image, int players) async {
  // Show the waiting screen
  Navigator.push(
    context,
    MaterialPageRoute(builder: (context) => const WaitingScreen()),
  );

  try {
    final uri = Uri.parse("${ApiConfig.baseUrl}/analyze/");
    final request = http.MultipartRequest('POST', uri);
    
    // Handle advice mode vs normal mode
    if (widget.isAdviceMode) {
      request.fields['players'] = 'advice';
    } else {
      request.fields['players'] = players.toString();
    }

    if (kIsWeb) {
      final bytes = await image.readAsBytes();
      final multipartFile = http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: image.name,
        contentType: MediaType('image', 'png'), // or 'png'
      );
      request.files.add(multipartFile);
    } else {
      request.files.add(await http.MultipartFile.fromPath('file', image.path));
    }

    final response = await request.send();

    if (response.statusCode == 200) {
      final responseBody = await response.stream.bytesToString();
      print("Backend response: $responseBody");

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ResultsScreen(
            resultsJson: responseBody,
            originalImage: image,
            players: players,
            isAdviceMode: widget.isAdviceMode,
          ),
        ),
      );
    } else {
      print("Error: ${response.statusCode}");
      Navigator.pop(context);
      _showErrorDialog("Server error: ${response.statusCode}");
    }
  } catch (e) {
    print("Upload exception: $e");
    Navigator.pop(context);
    _showErrorDialog("Upload failed. Is the backend running?");
  }
}



void _showErrorDialog(String message) {
  showDialog(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text("Error"),
      content: Text(message),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(ctx),
          child: const Text("OK"),
        ),
      ],
    ),
  );
}


  Future<void> _pickImageFromGallery() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      await _uploadImage(image, widget.players);
    }
  }

  Future<void> _captureWebImage() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.camera);
    if (image != null) {
      setState(() {
        _webImage = image;
      });
      await _uploadImage(image, widget.players);
    }
  }

  Future<void> _captureMobileImage() async {
    if (!kIsWeb && (io.Platform.isAndroid || io.Platform.isIOS)) {
      try {
        await _initializeControllerFuture;
        final image = await _controller.takePicture();
        await _uploadImage(image, widget.players);
      } catch (e) {
        _showErrorDialog("Error capturing image: $e");
      }
    }
  }

  Widget _buildOverlay(Size screenSize) {
    final height = screenSize.height;
    final width = screenSize.width;

    // Special overlay for advice mode
    if (widget.isAdviceMode) {
      return Positioned(
        bottom: 120,
        left: 24,
        right: 24,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Color(0xFF10B981).withOpacity(0.9),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            'Position your cards in the frame',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      );
    }

    // Normal overlay for 1-2 players
    return Stack(
      children: [
        // Dealer area
        Positioned(
          top: 60,
          left: 24,
          right: 24,
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.8),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              'Dealer Cards',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
        
        // Player areas
        Positioned(
          bottom: 120,
          left: 24,
          right: 24,
          child: Row(
            children: [
              if (widget.players == 1)
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Color(0xFF10B981).withOpacity(0.8),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Player 1',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                )
              else ...[
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Color(0xFF10B981).withOpacity(0.8),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Player 1',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.8),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Player 2',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    if (!kIsWeb && (io.Platform.isAndroid || io.Platform.isIOS)) {
      _controller.dispose();
    }
    super.dispose();
  }

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
                ],
              ),
            ),
            
            // Content
            Expanded(
              child: kIsWeb
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.photo_camera_rounded,
                              size: 64,
                              color: Color(0xFF10B981),
                            ),
                            const SizedBox(height: 32),
                            Text(
                              'Capture Cards',
                              style: TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              widget.isAdviceMode 
                                ? 'Take a photo of your cards\nfor AI advice'
                                : 'Position cards clearly in frame',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.white60,
                              ),
                            ),
                            const SizedBox(height: 48),
                            SizedBox(
                              width: double.infinity,
                              height: 56,
                              child: ElevatedButton(
                                onPressed: _captureWebImage,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Color(0xFF10B981),
                                  foregroundColor: Colors.white,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                  elevation: 0,
                                ),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.camera_alt_rounded, size: 22),
                                    const SizedBox(width: 12),
                                    Text(
                                      'Open Camera',
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                  : FutureBuilder(
                      future: _initializeControllerFuture,
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.done) {
                          return Stack(
                            children: [
                              // Camera preview
                              Positioned.fill(
                                child: cam.CameraPreview(_controller),
                              ),
                              
                              // Overlay
                              _buildOverlay(MediaQuery.of(context).size),
                              
                              // Bottom buttons
                              Positioned(
                                bottom: 40,
                                left: 0,
                                right: 0,
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    _buildCameraButton(
                                      Icons.photo_library_rounded,
                                      _pickImageFromGallery,
                                    ),
                                    const SizedBox(width: 24),
                                    _buildCameraButton(
                                      Icons.camera_alt_rounded,
                                      _captureMobileImage,
                                      isPrimary: true,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          );
                        } else {
                          return const Center(
                            child: CircularProgressIndicator(
                              color: Color(0xFF10B981),
                            ),
                          );
                        }
                      },
                    ),
            ),
            
            // Connection Footer
            const ConnectionFooter(),
          ],
        ),
      ),
    ),
  );
}

Widget _buildCameraButton(IconData icon, VoidCallback onPressed, {bool isPrimary = false}) {
  return Container(
    width: isPrimary ? 64 : 56,
    height: isPrimary ? 64 : 56,
    decoration: BoxDecoration(
      color: isPrimary ? Color(0xFF10B981) : Colors.white.withOpacity(0.2),
      shape: BoxShape.circle,
      border: Border.all(
        color: Colors.white.withOpacity(0.3),
        width: 2,
      ),
    ),
    child: IconButton(
      icon: Icon(
        icon,
        color: Colors.white,
        size: isPrimary ? 28 : 24,
      ),
      onPressed: onPressed,
    ),
  );
}
}
