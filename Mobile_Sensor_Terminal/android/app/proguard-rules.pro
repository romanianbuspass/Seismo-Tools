# Flutter
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Bluetooth Serial
-keep class io.github.edufolly.flutterbluetoothserial.** { *; }

# USB Serial
-keep class com.felhr.usbserial.** { *; }

# Play Core (referenced by Flutter but not needed for non-Play Store builds)
-dontwarn com.google.android.play.core.**
