import 'dart:io' show Platform;

import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';

import '../main.dart';

class AboutScreen extends StatefulWidget {
  const AboutScreen({super.key});

  @override
  State<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends State<AboutScreen> {
  String _bluetoothStatus = 'Unknown';

  @override
  void initState() {
    super.initState();
    _checkBluetooth();
  }

  Future<void> _checkBluetooth() async {
    try {
      final state = await FlutterBluetoothSerial.instance.state;
      if (mounted) {
        setState(() {
          _bluetoothStatus = state == BluetoothState.STATE_ON ? 'Enabled' : 'Disabled';
        });
      }
    } catch (_) {
      if (mounted) setState(() => _bluetoothStatus = 'Unavailable');
    }
  }

  @override
  Widget build(BuildContext context) {
    final os = Platform.operatingSystem;
    final osVersion = Platform.operatingSystemVersion;
    final startedAt = appStartupTime?.toIso8601String() ?? 'N/A';

    return Scaffold(
      backgroundColor: const Color(0xFF0f172a),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0f172a),
        title: const Text('About'),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        children: [
          const SizedBox(height: 16),
          // Logo
          Center(
            child: Image.asset(
              'assets/Gaiacode.png',
              width: 120,
              height: 120,
            ),
          ),
          const SizedBox(height: 24),
          // App name
          const Center(
            child: Text(
              'GaiaCode Sensor Terminal',
              style: TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 4),
          Center(
            child: Text(
              'v$appVersion',
              style: const TextStyle(color: Color(0xFF0EADB2), fontSize: 16),
            ),
          ),
          const SizedBox(height: 32),

          // Device info section
          _sectionTitle('Device Info'),
          _infoTile(Icons.phone_android, 'Platform', os),
          _infoTile(Icons.info_outline, 'OS Version', osVersion),
          _infoTile(Icons.bluetooth, 'Bluetooth', _bluetoothStatus),
          _infoTile(Icons.access_time, 'Started', startedAt),

          const SizedBox(height: 24),
          _sectionTitle('Contact'),
          _infoTile(Icons.email_outlined, 'Support', 'support@gaiacode.com'),
          _infoTile(Icons.language, 'Website', 'www.gaiacode.com'),

          const SizedBox(height: 32),
          Center(
            child: OutlinedButton.icon(
              icon: const Icon(Icons.article_outlined),
              label: const Text('Open Source Licenses'),
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF0EADB2),
                side: const BorderSide(color: Color(0xFF0EADB2)),
              ),
              onPressed: () {
                showLicensePage(
                  context: context,
                  applicationName: 'GaiaCode Sensor Terminal',
                  applicationVersion: appVersion,
                );
              },
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          color: Colors.white38,
          fontSize: 12,
          fontWeight: FontWeight.bold,
          letterSpacing: 1.2,
        ),
      ),
    );
  }

  Widget _infoTile(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF0EADB2), size: 20),
          const SizedBox(width: 12),
          Text(label, style: const TextStyle(color: Colors.white54, fontSize: 14)),
          const Spacer(),
          Flexible(
            child: Text(
              value,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              textAlign: TextAlign.end,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
