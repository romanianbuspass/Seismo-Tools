import 'dart:async';
import 'dart:io' show Platform;

import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/connection_manager.dart';
import '../widgets/branding_header.dart';
import 'terminal_screen.dart';

class ConnectionScreen extends StatefulWidget {
  const ConnectionScreen({super.key});

  @override
  State<ConnectionScreen> createState() => _ConnectionScreenState();
}

class _ConnectionScreenState extends State<ConnectionScreen>
    with SingleTickerProviderStateMixin {
  final ConnectionManager _cm = ConnectionManager();
  late TabController _tabController;

  // Bluetooth
  List<BluetoothDevice> _bondedDevices = [];
  final List<BluetoothDiscoveryResult> _discoveredDevices = [];
  bool _isScanning = false;
  StreamSubscription<BluetoothDiscoveryResult>? _discoverySub;

  // USB
  List<dynamic> _usbDevices = [];

  // Settings
  int _baudRate = 9600;
  static const _baudRates = [9600, 19200, 38400, 57600, 115200];

  // Last connected
  String? _lastDeviceId;
  String? _lastTypeName;

  bool _connecting = false;
  bool _permissionsGranted = false;

  @override
  void initState() {
    super.initState();
    final isAndroid = _tryIsAndroid;
    _tabController = TabController(length: isAndroid ? 2 : 1, vsync: this);
    _checkPermissions();
    _loadLastConnected();
  }

  Future<void> _checkPermissions() async {
    if (!_tryIsAndroid) {
      setState(() => _permissionsGranted = true);
      _loadBondedDevices();
      return;
    }

    // Show explanation dialog first
    if (mounted) {
      await showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          backgroundColor: const Color(0xFF1e293b),
          title: const Text('Permissions Required',
              style: TextStyle(color: Colors.white)),
          content: const Text(
            'This app needs Bluetooth and Location permissions to discover and connect to nearby seismic sensors.\n\n'
            '• Bluetooth Scan & Connect — to find and pair with sensors\n'
            '• Location — required on Android 6-11 for Bluetooth discovery',
            style: TextStyle(color: Colors.white70),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Continue',
                  style: TextStyle(color: Color(0xFF0EADB2))),
            ),
          ],
        ),
      );
    }

    // Request permissions
    final statuses = await [
      Permission.bluetoothScan,
      Permission.bluetoothConnect,
      Permission.locationWhenInUse,
    ].request();

    final allGranted = statuses.values.every(
      (s) => s.isGranted || s.isLimited,
    );

    if (allGranted) {
      setState(() => _permissionsGranted = true);
      _loadBondedDevices();
      if (_tryIsAndroid) _loadUsbDevices();
    } else {
      setState(() => _permissionsGranted = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Permissions denied. Bluetooth features unavailable.'),
            action: SnackBarAction(
              label: 'Open Settings',
              onPressed: () => openAppSettings(),
            ),
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  bool get _tryIsAndroid {
    try {
      return Platform.isAndroid;
    } catch (_) {
      return false;
    }
  }

  Future<void> _loadLastConnected() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _lastDeviceId = prefs.getString('conn_device_id');
      _lastTypeName = prefs.getString('conn_type');
      final savedBaud = prefs.getInt('conn_baud_rate');
      if (savedBaud != null) _baudRate = savedBaud;
    });
  }

  Future<void> _loadBondedDevices() async {
    try {
      final bonded = await _cm.bluetooth.getBondedDevices();
      setState(() => _bondedDevices = bonded);
    } catch (_) {}
  }

  Future<void> _loadUsbDevices() async {
    try {
      final devices = await _cm.usb.listDevices();
      setState(() => _usbDevices = devices);
    } catch (_) {}
  }

  void _startScan() {
    setState(() {
      _isScanning = true;
      _discoveredDevices.clear();
    });
    _discoverySub = _cm.bluetooth.discoverDevices().listen(
      (result) {
        // Avoid duplicates
        final exists = _discoveredDevices.any(
          (d) => d.device.address == result.device.address,
        );
        if (!exists) setState(() => _discoveredDevices.add(result));
      },
      onDone: () => setState(() => _isScanning = false),
      onError: (_) => setState(() => _isScanning = false),
    );
  }

  void _stopScan() {
    _discoverySub?.cancel();
    setState(() => _isScanning = false);
  }

  Future<void> _connectBluetooth(String address) async {
    setState(() => _connecting = true);
    try {
      await _cm.connect(ConnectionType.bluetooth, address, _baudRate);
      // Send sign-on query to auto-detect sensor type
      await Future.delayed(const Duration(milliseconds: 300));
      await _cm.activeService?.send('?', addCrlf: true);
      if (mounted) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => TerminalScreen(connectionManager: _cm),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Connection failed: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _connecting = false);
    }
  }

  Future<void> _connectUsb(String deviceId) async {
    setState(() => _connecting = true);
    try {
      await _cm.connect(ConnectionType.usb, deviceId, _baudRate);
      // Send sign-on query to auto-detect sensor type
      await Future.delayed(const Duration(milliseconds: 300));
      await _cm.activeService?.send('?', addCrlf: true);
      if (mounted) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => TerminalScreen(connectionManager: _cm),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Connection failed: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _connecting = false);
    }
  }

  Future<void> _quickReconnect() async {
    if (_lastDeviceId == null || _lastTypeName == null) return;
    setState(() => _connecting = true);
    try {
      final ok = await _cm.autoReconnect();
      if (ok && mounted) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => TerminalScreen(connectionManager: _cm),
          ),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Reconnection failed')),
        );
      }
    } finally {
      if (mounted) setState(() => _connecting = false);
    }
  }

  Widget _statusDot() {
    final color = _connecting
        ? Colors.amber
        : _cm.isConnected
            ? Colors.greenAccent
            : Colors.redAccent;
    return Container(
      width: 12,
      height: 12,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        boxShadow: [BoxShadow(color: color.withOpacity(0.6), blurRadius: 6)],
      ),
    );
  }

  Widget _bluetoothTab() {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      children: [
        // Scan button
        Row(
          children: [
            const Text('Bluetooth Devices',
                style: TextStyle(color: Colors.white70, fontSize: 16, fontWeight: FontWeight.bold)),
            const Spacer(),
            _isScanning
                ? IconButton(
                    icon: const Icon(Icons.stop, color: Colors.redAccent),
                    onPressed: _stopScan,
                  )
                : ElevatedButton.icon(
                    icon: const Icon(Icons.bluetooth_searching, size: 18),
                    label: const Text('Scan'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0EADB2),
                    ),
                    onPressed: _permissionsGranted ? _startScan : null,
                  ),
          ],
        ),
        if (_isScanning) const LinearProgressIndicator(color: Color(0xFF0EADB2)),
        const SizedBox(height: 8),

        // Bonded devices
        if (_bondedDevices.isNotEmpty) ...[
          const Text('Paired', style: TextStyle(color: Colors.white38, fontSize: 12)),
          ..._bondedDevices.map((d) => _deviceTile(
                d.name ?? 'Unknown',
                d.address,
                Icons.bluetooth_connected,
                () => _connectBluetooth(d.address),
              )),
          const SizedBox(height: 12),
        ],

        // Discovered devices
        if (_discoveredDevices.isNotEmpty) ...[
          const Text('Discovered', style: TextStyle(color: Colors.white38, fontSize: 12)),
          ..._discoveredDevices.map((r) => _deviceTile(
                r.device.name ?? 'Unknown',
                r.device.address,
                Icons.bluetooth,
                () => _connectBluetooth(r.device.address),
                rssi: r.rssi,
              )),
        ],

        if (_bondedDevices.isEmpty && _discoveredDevices.isEmpty)
          const Padding(
            padding: EdgeInsets.only(top: 32),
            child: Center(
              child: Text(
                'No devices found.\nTap Scan to discover nearby sensors.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white24),
              ),
            ),
          ),
      ],
    );
  }

  Widget _usbTab() {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      children: [
        Row(
          children: [
            const Text('USB Devices',
                style: TextStyle(color: Colors.white70, fontSize: 16, fontWeight: FontWeight.bold)),
            const Spacer(),
            IconButton(
              icon: const Icon(Icons.refresh, color: Color(0xFF0EADB2)),
              onPressed: _loadUsbDevices,
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (_usbDevices.isEmpty)
          const Padding(
            padding: EdgeInsets.only(top: 32),
            child: Center(
              child: Text(
                'No USB devices detected.\nConnect a sensor via USB OTG.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white24),
              ),
            ),
          ),
        ..._usbDevices.map((d) => _deviceTile(
              (d.productName as String?) ?? 'USB Device',
              d.deviceId.toString(),
              Icons.usb,
              () => _connectUsb(d.deviceId.toString()),
            )),
      ],
    );
  }

  Widget _deviceTile(
    String name,
    String address,
    IconData icon,
    VoidCallback onTap, {
    int? rssi,
  }) {
    return Card(
      color: const Color(0xFF293548),
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        leading: Icon(icon, color: const Color(0xFF0EADB2)),
        title: Text(name, style: const TextStyle(color: Colors.white)),
        subtitle: Text(address, style: const TextStyle(color: Colors.white38, fontSize: 12)),
        trailing: rssi != null
            ? Text('${rssi}dBm', style: const TextStyle(color: Colors.white38, fontSize: 12))
            : null,
        onTap: (_connecting || !_permissionsGranted) ? null : onTap,
      ),
    );
  }

  @override
  void dispose() {
    _discoverySub?.cancel();
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1e293b),
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 16),
            const BrandingHeader(),
            const SizedBox(height: 16),

            // Status & baud rate row
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  _statusDot(),
                  const SizedBox(width: 8),
                  Text(
                    _connecting ? 'Connecting…' : 'Disconnected',
                    style: const TextStyle(color: Colors.white54),
                  ),
                  const Spacer(),
                  // Baud rate
                  const Text('Baud:', style: TextStyle(color: Colors.white54, fontSize: 12)),
                  const SizedBox(width: 4),
                  DropdownButton<int>(
                    value: _baudRate,
                    dropdownColor: const Color(0xFF293548),
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                    underline: const SizedBox(),
                    items: _baudRates
                        .map((b) => DropdownMenuItem(value: b, child: Text('$b')))
                        .toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _baudRate = v);
                    },
                  ),
                ],
              ),
            ),

            // Quick reconnect
            if (_lastDeviceId != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.replay, size: 18),
                    label: Text('Reconnect (${_lastTypeName ?? ""}: ${_lastDeviceId!.substring(0, _lastDeviceId!.length.clamp(0, 12))}…)'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF0EADB2),
                      side: const BorderSide(color: Color(0xFF0EADB2)),
                    ),
                    onPressed: _connecting ? null : _quickReconnect,
                  ),
                ),
              ),

            // Tabs
            TabBar(
              controller: _tabController,
              indicatorColor: const Color(0xFF0EADB2),
              labelColor: const Color(0xFF0EADB2),
              unselectedLabelColor: Colors.white38,
              tabs: [
                const Tab(icon: Icon(Icons.bluetooth), text: 'Bluetooth'),
                if (_tryIsAndroid) const Tab(icon: Icon(Icons.usb), text: 'USB'),
              ],
            ),

            // Tab content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _bluetoothTab(),
                  if (_tryIsAndroid) _usbTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
