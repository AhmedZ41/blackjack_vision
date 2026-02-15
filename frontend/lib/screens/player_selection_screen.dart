import 'package:flutter/material.dart';
import 'camera_screen.dart';
import '../widgets/connection_footer.dart';

class PlayerSelectionScreen extends StatelessWidget {
  const PlayerSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    
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
                child: Padding(
                  padding: EdgeInsets.symmetric(
                    horizontal: screenWidth > 600 ? 64.0 : 32.0,
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Title
                      ShaderMask(
                        shaderCallback: (bounds) => LinearGradient(
                          colors: [
                            Color(0xFF10B981),
                            Color(0xFF06B6D4),
                          ],
                        ).createShader(bounds),
                        child: Text(
                          'Select Mode',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                            letterSpacing: -0.5,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      
                      Text(
                        'Choose number of players or get AI advice',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white60,
                          fontWeight: FontWeight.w400,
                        ),
                      ),
                      
                      const SizedBox(height: 60),
                      
                      // Buttons
                      _buildOptionButton(
                        context,
                        '1 Player',
                        Icons.person_rounded,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const CameraScreen(players: 1),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      _buildOptionButton(
                        context,
                        '2 Players',
                        Icons.people_rounded,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const CameraScreen(players: 2),
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      
                      _buildOptionButton(
                        context,
                        'AI Advice',
                        Icons.psychology_rounded,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const CameraScreen(
                              players: 0,
                              isAdviceMode: true,
                            ),
                          ),
                        ),
                        isPrimary: true,
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // Connection Footer
                      const ConnectionFooter(),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildOptionButton(
    BuildContext context,
    String label,
    IconData icon,
    VoidCallback onPressed, {
    bool isPrimary = false,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: isPrimary ? Color(0xFF10B981) : Colors.white.withOpacity(0.1),
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: isPrimary 
              ? BorderSide.none 
              : BorderSide(color: Colors.white.withOpacity(0.2)),
          ),
          elevation: 0,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 22),
            const SizedBox(width: 12),
            Text(
              label,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
