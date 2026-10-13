import 'package:flutter/material.dart';

/// Reusable GaiaCode branding header with logo and URL.
class BrandingHeader extends StatelessWidget {
  final double logoHeight;

  const BrandingHeader({super.key, this.logoHeight = 64});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Image.asset(
          'assets/Gaiacode.png',
          height: logoHeight,
          errorBuilder: (_, __, ___) => Icon(
            Icons.sensors,
            size: logoHeight,
            color: const Color(0xFF0EADB2),
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'www.gaiacode.com',
          style: TextStyle(
            color: Colors.grey,
            fontSize: 12,
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }
}
