import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class ConnectionFooter extends StatefulWidget {
  const ConnectionFooter({super.key});

  @override
  State<ConnectionFooter> createState() => _ConnectionFooterState();
}

class _ConnectionFooterState extends State<ConnectionFooter> {
  bool _isChecking = false;
  String? _connectionStatus;

  Future<void> _checkConnection() async {
    setState(() {
      _isChecking = true;
      _connectionStatus = null;
    });

    try {
      final response = await http.get(
        Uri.parse("${ApiConfig.baseUrl}/"),
      ).timeout(const Duration(seconds: 5));

      setState(() {
        _isChecking = false;
        if (response.statusCode == 200) {
          _connectionStatus = "✓ Connected";
        } else {
          _connectionStatus = "✗ Error ${response.statusCode}";
        }
      });

      // Clear status after 3 seconds
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            _connectionStatus = null;
          });
        }
      });
    } catch (e) {
      setState(() {
        _isChecking = false;
        _connectionStatus = "✗ Failed";
      });

      // Clear status after 3 seconds
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            _connectionStatus = null;
          });
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextButton.icon(
            onPressed: _isChecking ? null : _checkConnection,
            icon: _isChecking
                ? const SizedBox(
                    width: 12,
                    height: 12,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white54),
                    ),
                  )
                : const Icon(
                    Icons.wifi_rounded,
                    size: 14,
                    color: Colors.white54,
                  ),
            label: Text(
              _connectionStatus ?? 'Check Backend',
              style: const TextStyle(
                fontSize: 11,
                color: Colors.white54,
                fontWeight: FontWeight.w500,
              ),
            ),
            style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
          ),
        ],
      ),
    );
  }
}
