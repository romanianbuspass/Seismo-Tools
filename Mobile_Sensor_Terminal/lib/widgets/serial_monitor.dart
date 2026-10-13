import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:intl/intl.dart';

/// Type of terminal line for colour coding.
enum LineType { rx, tx, system }

class TerminalLine {
  final String text;
  final LineType type;
  final DateTime timestamp;

  TerminalLine(this.text, this.type) : timestamp = DateTime.now();
}

/// Terminal-style scrollable text display with RX/TX colour coding.
class SerialMonitor extends StatefulWidget {
  final Stream<String>? dataStream;
  final bool showTimestamps;

  const SerialMonitor({
    super.key,
    this.dataStream,
    this.showTimestamps = false,
  });

  @override
  State<SerialMonitor> createState() => SerialMonitorState();
}

class SerialMonitorState extends State<SerialMonitor> {
  static const int _maxLines = 5000;
  static const _bgColor = Color(0xFF0f172a);
  static const _rxColor = Color(0xFF4ade80);
  static const _txColor = Color(0xFF38bdf8);
  static const _sysColor = Color(0xFFfbbf24);
  static const _tsColor = Colors.grey;

  final List<TerminalLine> _lines = [];
  final ScrollController _scrollController = ScrollController();
  StreamSubscription<String>? _sub;
  final _tsFormat = DateFormat('HH:mm:ss.SSS');

  @override
  void initState() {
    super.initState();
    _subscribe();
  }

  @override
  void didUpdateWidget(SerialMonitor oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.dataStream != widget.dataStream) {
      _sub?.cancel();
      _subscribe();
    }
  }

  void _subscribe() {
    _sub = widget.dataStream?.listen((data) {
      addLine(data, LineType.rx);
    });
  }

  /// Add a line externally (e.g. TX echo or system message).
  void addLine(String text, LineType type) {
    if (!mounted) return;
    setState(() {
      _lines.add(TerminalLine(text, type));
      if (_lines.length > _maxLines) {
        _lines.removeRange(0, _lines.length - _maxLines);
      }
    });
    _scrollToBottom();
  }

  void clear() {
    setState(() => _lines.clear());
  }

  Future<String?> saveLog() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final file = File(
        '${dir.path}/sensor_log_${DateTime.now().millisecondsSinceEpoch}.txt',
      );
      final buf = StringBuffer();
      for (final line in _lines) {
        final prefix = line.type == LineType.tx
            ? 'TX'
            : line.type == LineType.system
                ? 'SYS'
                : 'RX';
        buf.writeln('[${_tsFormat.format(line.timestamp)}] $prefix: ${line.text}');
      }
      await file.writeAsString(buf.toString());
      return file.path;
    } catch (e) {
      return null;
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 100),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    _scrollController.dispose();
    super.dispose();
  }

  Color _colorFor(LineType type) {
    switch (type) {
      case LineType.tx:
        return _txColor;
      case LineType.system:
        return _sysColor;
      case LineType.rx:
        return _rxColor;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Header actions
        Container(
          color: const Color(0xFF1e293b),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: Row(
            children: [
              const Text(
                'Terminal',
                style: TextStyle(
                  color: Colors.white70,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.delete_outline, color: Colors.white54, size: 20),
                tooltip: 'Clear',
                onPressed: clear,
              ),
              IconButton(
                icon: const Icon(Icons.save_alt, color: Colors.white54, size: 20),
                tooltip: 'Save Log',
                onPressed: () async {
                  final path = await saveLog();
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(path != null ? 'Log saved: $path' : 'Save failed'),
                      ),
                    );
                  }
                },
              ),
            ],
          ),
        ),
        // Terminal body
        Expanded(
          child: Container(
            width: double.infinity,
            color: _bgColor,
            child: _lines.isEmpty
                ? const Center(
                    child: Text(
                      'No data yet. Connect to a sensor.',
                      style: TextStyle(color: Colors.white24, fontFamily: 'RobotoMono'),
                    ),
                  )
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(8),
                    itemCount: _lines.length,
                    itemBuilder: (_, i) {
                      final line = _lines[i];
                      return Text.rich(
                        TextSpan(
                          children: [
                            if (widget.showTimestamps)
                              TextSpan(
                                text: '${_tsFormat.format(line.timestamp)}  ',
                                style: const TextStyle(
                                  color: _tsColor,
                                  fontStyle: FontStyle.italic,
                                  fontSize: 12,
                                ),
                              ),
                            TextSpan(
                              text: line.text,
                              style: TextStyle(color: _colorFor(line.type)),
                            ),
                          ],
                        ),
                        style: const TextStyle(
                          fontFamily: 'RobotoMono',
                          fontSize: 13,
                          height: 1.4,
                        ),
                      );
                    },
                  ),
          ),
        ),
      ],
    );
  }
}
