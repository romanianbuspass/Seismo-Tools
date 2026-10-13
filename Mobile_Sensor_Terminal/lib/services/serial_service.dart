/// Abstract serial communication interface for the Sensor Terminal.
abstract class SerialService {
  /// Stream of decoded string data received from the device.
  Stream<String> get dataStream;

  /// Connect to a device by [deviceId] at [baudRate].
  Future<void> connect(String deviceId, int baudRate);

  /// Disconnect from the current device and release resources.
  Future<void> disconnect();

  /// Send a [command] string to the connected device.
  /// If [addCrlf] is true (default), appends \r\n.
  Future<void> send(String command, {bool addCrlf = true});

  /// Whether a device is currently connected.
  bool get isConnected;

  /// Human-readable description of the current connection.
  String get connectionInfo;
}

/// Connection lifecycle states.
enum ConnectionState {
  disconnected,
  scanning,
  connecting,
  connected,
}
