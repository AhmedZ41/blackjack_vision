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






class CameraScreen extends StatefulWidget {
  final int players;
  const CameraScreen({super.key, required this.players});

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
        _showErrorDialog("✅ Backend connection successful!\nURL: ${ApiConfig.baseUrl}");
      } else {
        _showErrorDialog("❌ Backend responded with status: ${response.statusCode}");
      }
    } catch (e) {
      _showErrorDialog("❌ Cannot connect to backend\nURL: ${ApiConfig.baseUrl}\nError: $e");
    }
  }


Future<void> _uploadImage(XFile image, int players) async {
  // Show the waiting screen
  Navigator.push(
    context,
    MaterialPageRoute(builder: (context) => const WaitingScreen()),
  );

  try {
    final uri = Uri.parse("http://192.168.178.26:8000/analyze/");
    final request = http.MultipartRequest('POST', uri)
      ..fields['players'] = players.toString();

    if (kIsWeb) {
      final bytes = await image.readAsBytes();
      final multipartFile = http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: image.name,
        contentType: MediaType('image', 'jpeg'), // or 'png'
      );
      request.files.add(multipartFile);
    } else {
      request.files.add(await http.MultipartFile.fromPath('file', image.path));
    }

    final response = await request.send();

    if (response.statusCode == 200) {
      final responseBody = await response.stream.bytesToString();
      print("✅ Backend response: $responseBody");

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ResultsScreen(resultsJson: responseBody),
        ),
      );
    } else {
      print("❌ Error: ${response.statusCode}");
      Navigator.pop(context);
      _showErrorDialog("Server error: ${response.statusCode}");
    }
  } catch (e) {
    print("❌ Upload exception: $e");
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

  Widget _buildOverlay(BoxConstraints constraints) {
    final height = constraints.maxHeight;
    final width = constraints.maxWidth;

    return Stack(
      children: [
        Positioned(
          top: 0,
          left: 0,
          width: width,
          height: height / 2,
          child: Container(
            color: Colors.blue.withOpacity(0.2),
            alignment: Alignment.topCenter,
            child: const Padding(
              padding: EdgeInsets.all(8.0),
              child: Text('Dealer', style: TextStyle(color: Colors.white)),
            ),
          ),
        ),
        if (widget.players == 1)
          Positioned(
            top: height / 2,
            left: 0,
            width: width,
            height: height / 2,
            child: Container(
              color: Colors.green.withOpacity(0.2),
              alignment: Alignment.bottomCenter,
              child: const Padding(
                padding: EdgeInsets.all(8.0),
                child: Text('Player 1', style: TextStyle(color: Colors.white)),
              ),
            ),
          )
        else ...[
          Positioned(
            top: height / 2,
            left: 0,
            width: width / 2,
            height: height / 2,
            child: Container(
              color: Colors.green.withOpacity(0.2),
              alignment: Alignment.bottomLeft,
              child: const Padding(
                padding: EdgeInsets.all(8.0),
                child: Text('Player 1', style: TextStyle(color: Colors.white)),
              ),
            ),
          ),
          Positioned(
            top: height / 2,
            left: width / 2,
            width: width / 2,
            height: height / 2,
            child: Container(
              color: Colors.orange.withOpacity(0.2),
              alignment: Alignment.bottomRight,
              child: const Padding(
                padding: EdgeInsets.all(8.0),
                child: Text('Player 2', style: TextStyle(color: Colors.white)),
              ),
            ),
          ),
        ]
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
    backgroundColor: Colors.black,
    body: kIsWeb
        ? Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (_webImage != null)
                  Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.greenAccent, width: 2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Image.network(_webImage!.path, width: 300),
                  ),
                const SizedBox(height: 60),
                _retroButton("Open Camera", _captureWebImage),
                const SizedBox(height: 10),
                _retroButton("Upload Image", _pickImageFromGallery),
                //const SizedBox(height: 10),
                //_retroButton("Test Backend Connection", _testConnection),
              ],
            ),
          )
        : FutureBuilder(
            future: _initializeControllerFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.done) {
                return LayoutBuilder(
                  builder: (context, constraints) {
                    return Stack(
                      children: [
                        cam.CameraPreview(_controller),
                        _buildOverlay(constraints),
                        Positioned(
                          bottom: 30,
                          left: MediaQuery.of(context).size.width / 2 - 90,
                          child: Row(
                            children: [
                              _fabRetro(Icons.camera_alt, _captureMobileImage),
                              const SizedBox(width: 20),
                              _fabRetro(Icons.photo_library, _pickImageFromGallery),
                            ],
                          ),
                        ),
                        Positioned(
                          top: 50,
                          right: 20,
                          child: _retroButton("Test Connection", _testConnection),
                        ),
                      ],
                    );
                  },
                );
              } else {
                return const Center(child: CircularProgressIndicator(color: Colors.greenAccent));
              }
            },
          ),
  );
}

Widget _retroButton(String label, VoidCallback onPressed) {
  return ElevatedButton(
    onPressed: onPressed,
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.black,
      foregroundColor: Colors.greenAccent,
      shadowColor: Colors.greenAccent,
      elevation: 8,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: const BorderSide(color: Colors.greenAccent),
      ),
    ),
    child: Text(
      label,
      style: const TextStyle(
        fontFamily: 'Courier',
        fontSize: 14,
        letterSpacing: 1.5,
        fontWeight: FontWeight.w600,
      ),
    ),
  );
}

Widget _fabRetro(IconData icon, VoidCallback onPressed) {
  return FloatingActionButton(
    backgroundColor: Colors.black,
    foregroundColor: Colors.greenAccent,
    shape: const StadiumBorder(side: BorderSide(color: Colors.greenAccent)),
    onPressed: onPressed,
    child: Icon(icon),
  );
}
}
