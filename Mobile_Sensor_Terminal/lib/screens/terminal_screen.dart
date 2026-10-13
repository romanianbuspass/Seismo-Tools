import 'dart:async';

import 'package:flutter/material.dart';

import '../models/sensor_profiles.dart';
import '../services/connection_manager.dart';
import '../widgets/command_grid.dart';
import '../widgets/serial_monitor.dart';
import 'about_screen.dart';

class TerminalScreen extends StatefulWidget {
  final ConnectionManager connectionManager;

  const TerminalScreen({super.key, required this.connectionManager});

  @override
  State<TerminalScreen> createState() => _TerminalScreenState();
}

class _TerminalScreenState extends State<TerminalScreen> {
  final _cmdController = TextEditingController();
  final _monitorKey = GlobalKey<SerialMonitorState>();

  String _profileKey = 'pico';
  bool _addCrlf = true;
  bool _showTimestamps = false;
  String? _pendingCommandLabel; // Tracks last command sent for acknowledgment
  String? _pendingCommandCmd;   // The actual command character sent
  StreamSubscription<String>? _ackSubscription;
  int _pendingResponseLines = 0; // For multi-line responses
  final List<String> _pendingResponseBuffer = []; // Collect multi-line responses

  ConnectionManager get _cm => widget.connectionManager;

  SensorProfile get _profile => SensorProfile.getProfile(_profileKey);

  static const _profileKeys = ['pico', 'theta', 'sigma', 'alpha'];

  @override
  void initState() {
    super.initState();
    _listenForAcknowledgments();
  }

  /// Commands that return multi-line responses — wait for all lines before showing feedback.
  /// Maps command char → expected number of response lines.
  static const _multiLineCommands = {
    '?': 4,  // Sign-On: varies by sensor but collect 4 lines
    'D': 8,  // Show Params: Centre Limits + axes data
  };

  /// Lines to silently ignore from acknowledgment snackbar (but still show in terminal).
  static const _ignoreForAck = ['Wake', 'Sleep'];

  /// Sensor name patterns in sign-on messages for auto-detection.
  static const _sensorDetectMap = {
    'ALPHA': 'alpha',
    'Theta': 'theta',
    'SIGMA': 'sigma',
  };

  /// Auto-detect sensor profile from a sign-on response line.
  void _tryAutoDetectSensor(String line) {
    if (!line.startsWith('GAIA')) return;
    for (final entry in _sensorDetectMap.entries) {
      if (line.contains(entry.key)) {
        if (_profileKey != entry.value) {
          setState(() => _profileKey = entry.value);
          // Also check for Pico vs Standard Theta
          if (entry.value == 'theta' && line.contains('Pico')) {
            setState(() => _profileKey = 'pico');
          }
          _monitorKey.currentState?.addLine(
            '⚙ Auto-detected: ${_profile.name}', LineType.system,
          );
        }
        return;
      }
    }
  }

  void _listenForAcknowledgments() {
    _ackSubscription = _cm.dataStream?.listen((line) {
      final trimmed = line.trim();

      // Try auto-detecting sensor from any GAIA line
      _tryAutoDetectSensor(trimmed);

      // Skip Wake/Sleep for acknowledgment feedback only
      if (_ignoreForAck.contains(trimmed)) return;

      // If collecting multi-line response, keep buffering
      if (_pendingResponseLines > 0) {
        _pendingResponseBuffer.add(trimmed);
        _pendingResponseLines--;
        if (_pendingResponseLines <= 0) {
          // All lines collected — show combined feedback
          _showAckSnackbar(_pendingResponseBuffer.join('\n'));
          _pendingResponseBuffer.clear();
          _pendingCommandLabel = null;
          _pendingCommandCmd = null;
        }
        return;
      }

      if (_pendingCommandLabel == null || _pendingCommandCmd == null) return;
      if (!mounted) return;

      final cmd = _pendingCommandCmd!;

      // Check if this is a multi-line command starting
      if (_multiLineCommands.containsKey(cmd)) {
        // Sign-on line count varies by sensor
        int expectedLines = _multiLineCommands[cmd]!;
        if (cmd == '?') {
          // Alpha & Sigma sign-on is 1-2 lines, Theta is 4
          if (trimmed.contains('ALPHA') || trimmed.contains('SIGMA')) {
            expectedLines = 2;
          } else {
            expectedLines = 4; // Theta: GAIA, Mems, T P H, Mag
          }
        }
        _pendingResponseBuffer.clear();
        _pendingResponseBuffer.add(trimmed);
        _pendingResponseLines = expectedLines - 1;
        if (_pendingResponseLines <= 0) {
          _showAckSnackbar(_pendingResponseBuffer.join('\n'));
          _pendingResponseBuffer.clear();
          _pendingCommandLabel = null;
          _pendingCommandCmd = null;
        }
        return;
      }

      // Single-line response — match by command
      String feedback;
      switch (cmd) {
        case 'A':
          feedback = 'All Axes selected';
          break;
        case 'N':
          feedback = 'North/South axis selected';
          break;
        case 'E':
          feedback = 'East/West axis selected';
          break;
        case 'Z':
          feedback = 'Vertical axis selected';
          break;
        case 'C':
          feedback = trimmed.replaceAll(RegExp(r'^c'), '');
          break;
        case 'M':
        case '<':
        case '>':
          feedback = trimmed.replaceAll(RegExp(r'^[m<>]'), '');
          break;
        case '=':
          feedback = trimmed.isNotEmpty ? trimmed : 'Zero Mass Position set';
          break;
        case 'I':
          feedback = 'Calibration enabled';
          break;
        case 'K':
          feedback = 'Calibration disabled';
          break;
        case 'G':
          feedback = 'Low Gain set';
          break;
        case 'H':
          feedback = 'High Gain set';
          break;
        case '1G':
          feedback = '0.5g Gain set';
          break;
        case '2G':
          feedback = '1g Gain set';
          break;
        case '3G':
          feedback = '2g Gain set';
          break;
        case '4G':
          feedback = '4g Gain set';
          break;
        case 'S':
          feedback = 'Short Period mode';
          break;
        case 'B':
          feedback = 'Long Period mode';
          break;
        case 'Q':
          feedback = 'Parameters stored';
          break;
        case 'L':
          feedback = 'Axes locked';
          break;
        case 'U':
          feedback = 'Axes unlocked';
          break;
        default:
          feedback = '${_pendingCommandLabel}: $trimmed';
      }

      _showAckSnackbar(feedback);
      _pendingCommandLabel = null;
      _pendingCommandCmd = null;
    });
  }

  void _showAckSnackbar(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('✅ $message', maxLines: 6),
        backgroundColor: const Color(0xFF10b981),
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.only(bottom: 80, left: 16, right: 16),
      ),
    );
  }

  /// Look up the human-readable label for a command string.
  String _labelForCommand(String cmd) {
    for (final group in _profile.groups) {
      for (final button in group.buttons) {
        if (button.cmd == cmd) return button.label;
      }
    }
    return cmd; // Fallback to raw command
  }

  void _sendCommand(String cmd) async {
    if (!_cm.isConnected) {
      _monitorKey.currentState?.addLine('⚠ Not connected', LineType.system);
      return;
    }
    try {
      // Wake the sensor first — send a blank line to exit sleep mode
      await _cm.activeService!.send('', addCrlf: true);
      // Brief pause to let the sensor wake up
      await Future.delayed(const Duration(milliseconds: 150));

      _pendingCommandLabel = _labelForCommand(cmd);
      _pendingCommandCmd = cmd;
      _pendingResponseLines = 0;
      _pendingResponseBuffer.clear();
      await _cm.activeService!.send(cmd, addCrlf: _addCrlf);
      _monitorKey.currentState?.addLine('→ $cmd', LineType.tx);
    } catch (e) {
      _pendingCommandLabel = null;
      _pendingCommandCmd = null;
      _monitorKey.currentState?.addLine('⚠ Send error: $e', LineType.system);
    }
  }

  void _sendCustom() {
    final cmd = _cmdController.text.trim();
    if (cmd.isEmpty) return;
    _sendCommand(cmd);
    _cmdController.clear();
  }

  Future<void> _disconnect() async {
    await _cm.disconnect();
    if (mounted) Navigator.of(context).pop();
  }

  void _showSettings() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1e293b),
      builder: (_) => StatefulBuilder(
        builder: (ctx, setBS) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SwitchListTile(
                title: const Text('Append CR+LF', style: TextStyle(color: Colors.white)),
                value: _addCrlf,
                activeColor: const Color(0xFF0EADB2),
                onChanged: (v) {
                  setBS(() => _addCrlf = v);
                  setState(() {});
                },
              ),
              SwitchListTile(
                title: const Text('Show Timestamps', style: TextStyle(color: Colors.white)),
                value: _showTimestamps,
                activeColor: const Color(0xFF0EADB2),
                onChanged: (v) {
                  setBS(() => _showTimestamps = v);
                  setState(() {});
                },
              ),
              ListTile(
                leading: const Icon(Icons.delete_outline, color: Colors.white54),
                title: const Text('Clear Terminal', style: TextStyle(color: Colors.white)),
                onTap: () {
                  _monitorKey.currentState?.clear();
                  Navigator.pop(ctx);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _statusDot() {
    final color = _cm.isConnected ? Colors.greenAccent : Colors.redAccent;
    return Container(
      width: 10,
      height: 10,
      margin: const EdgeInsets.symmetric(horizontal: 6),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        boxShadow: [BoxShadow(color: color.withOpacity(0.6), blurRadius: 4)],
      ),
    );
  }

  Widget _buildBody(bool isWide) {
    final commandPanel = CommandGrid(
      profile: _profile,
      onCommandSend: _sendCommand,
    );

    final terminalPanel = SerialMonitor(
      key: _monitorKey,
      dataStream: _cm.dataStream,
      showTimestamps: _showTimestamps,
    );

    if (isWide) {
      // Side-by-side for tablets/landscape
      return Row(
        children: [
          Expanded(child: commandPanel),
          const VerticalDivider(width: 1, color: Colors.white12),
          Expanded(child: terminalPanel),
        ],
      );
    }

    // Tabbed for phone/portrait
    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          const TabBar(
            indicatorColor: Color(0xFF0EADB2),
            labelColor: Color(0xFF0EADB2),
            unselectedLabelColor: Colors.white38,
            tabs: [
              Tab(text: 'Commands'),
              Tab(text: 'Terminal'),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [commandPanel, terminalPanel],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _ackSubscription?.cancel();
    _cmdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isWide = MediaQuery.of(context).size.width >= 720;

    return Scaffold(
      backgroundColor: const Color(0xFF1e293b),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0f172a),
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _statusDot(),
            const SizedBox(width: 4),
            DropdownButton<String>(
              value: _profileKey,
              dropdownColor: const Color(0xFF293548),
              style: const TextStyle(color: Colors.white, fontSize: 16),
              underline: const SizedBox(),
              items: _profileKeys.map((k) {
                final p = SensorProfile.getProfile(k);
                return DropdownMenuItem(value: k, child: Text(p.name));
              }).toList(),
              onChanged: (v) {
                if (v != null) setState(() => _profileKey = v);
              },
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline, color: Colors.white54),
            tooltip: 'About',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const AboutScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings, color: Colors.white54),
            onPressed: _showSettings,
          ),
          IconButton(
            icon: const Icon(Icons.power_settings_new, color: Colors.redAccent),
            tooltip: 'Disconnect',
            onPressed: _disconnect,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(child: _buildBody(isWide)),
          // Bottom command input
          Container(
            color: const Color(0xFF0f172a),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _cmdController,
                    style: const TextStyle(
                      color: Colors.white,
                      fontFamily: 'RobotoMono',
                      fontSize: 14,
                    ),
                    decoration: InputDecoration(
                      hintText: 'Custom command…',
                      hintStyle: const TextStyle(color: Colors.white24),
                      filled: true,
                      fillColor: const Color(0xFF1e293b),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onSubmitted: (_) => _sendCustom(),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0EADB2),
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  ),
                  onPressed: _sendCustom,
                  child: const Text('SEND'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
