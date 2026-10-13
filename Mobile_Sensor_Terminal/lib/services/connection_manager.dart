import 'dart:async';

import 'package:shared_preferences/shared_preferences.dart';

import 'serial_service.dart';
import 'bluetooth_serial_service.dart';
import 'usb_serial_service.dart';

/// Available connection transports.
enum ConnectionType { bluetooth, usb }

/// Unified connection manager that wraps Bluetooth and USB serial services.
class ConnectionManager {
  final BluetoothSerialService _btService = BluetoothSerialService();
  final UsbSerialService _usbService = UsbSerialService();

  ConnectionType? _activeType;
  Timer? _timeoutTimer;
  StreamSubscription<String>? _dataWatchSub;

  /// Called when connection is lost unexpectedly.
  void Function()? onConnectionLost;

  // SharedPreferences keys
  static const _keyType = 'conn_type';
  static const _keyDeviceId = 'conn_device_id';
  static const _keyBaudRate = 'conn_baud_rate';

  /// The currently active serial service, or null if nothing is connected.
  SerialService? get activeService {
    switch (_activeType) {
      case ConnectionType.bluetooth:
        return _btService;
      case ConnectionType.usb:
        return _usbService;
      case null:
        return null;
    }
  }

  /// Convenience: the Bluetooth service for discovery/pairing UI.
  BluetoothSerialService get bluetooth => _btService;

  /// Convenience: the USB service for device listing UI.
  UsbSerialService get usb => _usbService;

  /// Unified data stream from whichever transport is active.
  Stream<String> get dataStream {
    return activeService?.dataStream ?? const Stream.empty();
  }

  /// Whether any transport is currently connected.
  bool get isConnected => activeService?.isConnected ?? false;

  /// Human-readable connection info.
  String get connectionInfo => activeService?.connectionInfo ?? 'No connection';

  /// Connect using the specified [type] transport.
  Future<void> connect(ConnectionType type, String deviceId, int baudRate) async {
    // Disconnect any existing connection first.
    await disconnect();

    _activeType = type;
    await activeService!.connect(deviceId, baudRate);

    // Persist for auto-reconnect.
    await _saveSettings(type, deviceId, baudRate);

    // Start connection timeout & loss monitoring.
    _startConnectionMonitoring();
  }

  /// Disconnect the current transport.
  Future<void> disconnect() async {
    _cancelMonitoring();
    await activeService?.disconnect();
    _activeType = null;
  }

  /// Disconnect current and prepare to use a different [type].
  /// Does not connect — call [connect] afterwards with device details.
  Future<void> switchConnection(ConnectionType type) async {
    await disconnect();
    _activeType = type;
  }

  /// Attempt to reconnect using the last saved settings.
  /// Returns true if reconnection succeeded.
  Future<bool> autoReconnect() async {
    final prefs = await SharedPreferences.getInstance();
    final typeName = prefs.getString(_keyType);
    final deviceId = prefs.getString(_keyDeviceId);
    final baudRate = prefs.getInt(_keyBaudRate);

    if (typeName == null || deviceId == null || baudRate == null) return false;

    final type = ConnectionType.values.firstWhere(
      (t) => t.name == typeName,
      orElse: () => ConnectionType.bluetooth,
    );

    try {
      await connect(type, deviceId, baudRate);
      return true;
    } catch (_) {
      return false;
    }
  }

  /// Reconnect using saved settings from SharedPreferences.
  /// Alias for [autoReconnect] for convenient use from UI.
  Future<bool> reconnect() => autoReconnect();

  /// Whether a connection timeout warning should be shown.
  /// Set to true if no data received within 10s of connecting.
  bool connectionTimedOut = false;

  /// Callback for connection timeout warning (no data within 10s).
  void Function()? onConnectionTimeout;

  void _startConnectionMonitoring() {
    _cancelMonitoring();
    connectionTimedOut = false;

    // Timeout: warn if no data within 10 seconds.
    _timeoutTimer = Timer(const Duration(seconds: 10), () {
      connectionTimedOut = true;
      onConnectionTimeout?.call();
    });

    // Cancel timeout on first data, monitor for connection loss.
    _dataWatchSub = dataStream.listen(
      (_) {
        if (_timeoutTimer?.isActive ?? false) {
          _timeoutTimer!.cancel();
          connectionTimedOut = false;
        }
      },
      onError: (_) {
        _cancelMonitoring();
        onConnectionLost?.call();
      },
      onDone: () {
        _cancelMonitoring();
        if (_activeType != null) {
          _activeType = null;
          onConnectionLost?.call();
        }
      },
    );
  }

  void _cancelMonitoring() {
    _timeoutTimer?.cancel();
    _timeoutTimer = null;
    _dataWatchSub?.cancel();
    _dataWatchSub = null;
  }

  Future<void> _saveSettings(ConnectionType type, String deviceId, int baudRate) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyType, type.name);
    await prefs.setString(_keyDeviceId, deviceId);
    await prefs.setInt(_keyBaudRate, baudRate);
  }

  /// Release all resources.
  Future<void> dispose() async {
    _cancelMonitoring();
    await _btService.dispose();
    await _usbService.dispose();
  }
}
