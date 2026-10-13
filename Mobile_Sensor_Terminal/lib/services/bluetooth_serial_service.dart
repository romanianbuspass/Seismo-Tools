import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';

import 'serial_service.dart';

/// Bluetooth Classic serial implementation using flutter_bluetooth_serial.
class BluetoothSerialService extends SerialService {
  final _dataController = StreamController<String>.broadcast();
  BluetoothConnection? _connection;
  StreamSubscription<Uint8List>? _inputSubscription;
  ConnectionState _state = ConnectionState.disconnected;
  String _deviceName = '';
  String _deviceAddress = '';
  String _lineBuffer = ''; // Accumulates partial data until newline

  ConnectionState get state => _state;

  @override
  Stream<String> get dataStream => _dataController.stream;

  @override
  bool get isConnected => _state == ConnectionState.connected && _connection != null;

  @override
  String get connectionInfo =>
      isConnected ? 'Bluetooth: $_deviceName ($_deviceAddress)' : 'Bluetooth: disconnected';

  /// Returns a list of already-bonded (paired) Bluetooth devices.
  Future<List<BluetoothDevice>> getBondedDevices() async {
    return FlutterBluetoothSerial.instance.getBondedDevices();
  }

  /// Starts Bluetooth discovery and yields results as they arrive.
  Stream<BluetoothDiscoveryResult> discoverDevices() {
    _state = ConnectionState.scanning;
    return FlutterBluetoothSerial.instance.startDiscovery();
  }

  @override
  Future<void> connect(String address, int baudRate) async {
    // baudRate is not configurable for BT Classic SPP — included for interface compat.
    if (isConnected) await disconnect();

    _state = ConnectionState.connecting;
    try {
      _connection = await BluetoothConnection.toAddress(address);
      _deviceAddress = address;

      // Try to resolve a friendly name from bonded list.
      try {
        final bonded = await getBondedDevices();
        _deviceName = bonded
            .firstWhere((d) => d.address == address,
                orElse: () => BluetoothDevice(address: address))
            .name ?? address;
      } catch (_) {
        _deviceName = address;
      }

      _state = ConnectionState.connected;

      _inputSubscription = _connection!.input?.listen(
        (data) {
          // Buffer incoming bytes and emit complete lines only
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
        onDone: () {
          _state = ConnectionState.disconnected;
          _dataController.addError(
            Exception('Bluetooth connection closed. Try reconnecting to $_deviceName.'),
          );
        },
        onError: (error) {
          _state = ConnectionState.disconnected;
          _dataController.addError(
            Exception('Bluetooth error: $error. Try reconnecting to $_deviceName.'),
          );
        },
        cancelOnError: false,
      );
    } catch (e) {
      _state = ConnectionState.disconnected;
      throw Exception(
        'Failed to connect to $address: $e. Ensure the device is paired and in range.',
      );
    }
  }

  @override
  Future<void> send(String command, {bool addCrlf = true}) async {
    if (!isConnected) throw Exception('Not connected via Bluetooth.');
    final payload = addCrlf ? '$command\r\n' : command;
    _connection!.output.add(Uint8List.fromList(utf8.encode(payload)));
    await _connection!.output.allSent;
  }

  @override
  Future<void> disconnect() async {
    await _inputSubscription?.cancel();
    _inputSubscription = null;

    try {
      await _connection?.close();
    } catch (_) {
      // Best-effort close.
    }
    _connection = null;
    _state = ConnectionState.disconnected;
    _lineBuffer = '';
  }

  /// Release all resources. Call when the service is no longer needed.
  Future<void> dispose() async {
    await disconnect();
    await _dataController.close();
  }
}
