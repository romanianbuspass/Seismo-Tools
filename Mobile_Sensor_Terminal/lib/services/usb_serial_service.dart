import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'dart:io' show Platform;

import 'package:usb_serial/usb_serial.dart';
import 'package:usb_serial/transaction.dart';

import 'serial_service.dart';

/// USB OTG serial implementation using the usb_serial package.
/// Only functional on Android; returns empty/no-op on iOS.
class UsbSerialService extends SerialService {
  final _dataController = StreamController<String>.broadcast();
  UsbPort? _port;
  StreamSubscription<Uint8List>? _inputSubscription;
  ConnectionState _state = ConnectionState.disconnected;
  String _deviceDescription = '';
  String _lineBuffer = ''; // Accumulates partial data until newline

  ConnectionState get state => _state;

  @override
  Stream<String> get dataStream => _dataController.stream;

  @override
  bool get isConnected => _state == ConnectionState.connected && _port != null;

  @override
  String get connectionInfo =>
      isConnected ? 'USB: $_deviceDescription' : 'USB: disconnected';

  bool get _isAndroid {
    try {
      return Platform.isAndroid;
    } catch (_) {
      return false;
    }
  }

  /// Lists attached USB serial devices. Returns empty on iOS.
  Future<List<UsbDevice>> listDevices() async {
    if (!_isAndroid) return [];
    return UsbSerial.listDevices();
  }

  @override
  Future<void> connect(String deviceId, int baudRate) async {
    if (!_isAndroid) {
      throw Exception('USB serial is only supported on Android.');
    }

    if (isConnected) await disconnect();
    _state = ConnectionState.connecting;

    try {
      final devices = await UsbSerial.listDevices();
      final device = devices.firstWhere(
        (d) => d.deviceId.toString() == deviceId || d.productName == deviceId,
        orElse: () => throw Exception('USB device "$deviceId" not found. Check connection.'),
      );

      _port = await device.create();
      if (_port == null) {
        throw Exception('Could not open USB port for device "$deviceId".');
      }

      final opened = await _port!.open();
      if (!opened) {
        _port = null;
        throw Exception('Failed to open USB port. Check permissions.');
      }

      await _port!.setDTR(true);
      await _port!.setRTS(true);
      await _port!.setPortParameters(
        baudRate,
        UsbPort.DATABITS_8,
        UsbPort.STOPBITS_1,
        UsbPort.PARITY_NONE,
      );

      _deviceDescription = device.productName ?? 'USB device $deviceId';
      _state = ConnectionState.connected;

      _inputSubscription = _port!.inputStream?.listen(
        (data) {
          _lineBuffer += utf8.decode(data, allowMalformed: true);
          while (_lineBuffer.contains('\n')) {
            final idx = _lineBuffer.indexOf('\n');
            final line = _lineBuffer.substring(0, idx).replaceAll('\r', '');
            _lineBuffer = _lineBuffer.substring(idx + 1);
            if (line.isNotEmpty) {
              _dataController.add(line);
            }
          }
        },
        onError: (error) {
          _state = ConnectionState.disconnected;
          _dataController.addError(Exception('USB read error: $error'));
        },
        onDone: () {
          _state = ConnectionState.disconnected;
        },
        cancelOnError: false,
      );
    } catch (e) {
      _state = ConnectionState.disconnected;
      rethrow;
    }
  }

  @override
  Future<void> send(String command, {bool addCrlf = true}) async {
    if (!isConnected) throw Exception('Not connected via USB.');
    final payload = addCrlf ? '$command\r\n' : command;
    await _port!.write(Uint8List.fromList(utf8.encode(payload)));
  }

  @override
  Future<void> disconnect() async {
    await _inputSubscription?.cancel();
    _inputSubscription = null;

    try {
      await _port?.close();
    } catch (_) {}
    _port = null;
    _state = ConnectionState.disconnected;
    _lineBuffer = '';
  }

  /// Release all resources.
  Future<void> dispose() async {
    await disconnect();
    await _dataController.close();
  }
}
