# GaiaCode Sensor Terminal — Mobile

<p align="center">
  <img src="assets/Gaiacode.png" alt="GaiaCode" width="200"/>
</p>

<p align="center">
  <strong>Universal Seismometer Control Terminal for Android & iOS</strong><br/>
  Bluetooth & USB OTG serial interface for GaiaCode seismic sensors
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#supported-sensors">Sensors</a> •
  <a href="#installation">Installation</a> •
  <a href="#building">Building</a> •
  <a href="#usage">Usage</a> •
  <a href="#command-reference">Commands</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#license">License</a>
</p>

---

## Features

### Connection
- **Bluetooth Serial** — Wireless connection via Bluetooth Classic (SPP)
- **USB OTG Serial** — Wired connection on Android devices with USB-C/micro-USB OTG adapters
- **Auto-detect sensor** — Automatically identifies connected sensor from sign-on message and loads correct profile
- **Wake-before-send** — Sends wake signal before each command to handle sensor sleep mode
- **Quick reconnect** — Remembers last connected device for one-tap reconnection
- **Default baud rate** — 9600 (configurable: 9600, 19200, 38400, 57600, 115200)

### Control Interface
- **4 sensor profiles** — Pre-configured command sets for Theta Pico, Theta Standard, Sigma, and Alpha
- **Instrument-panel UI** — Dark themed, touch-optimised command grid with Unicode icons and colour-coded groups
- **Smart acknowledgment** — Parses sensor responses and shows human-readable confirmation (e.g. "✅ Calibration enabled")
- **Multi-line response handling** — Collects full sign-on messages and parameter dumps before displaying
- **Haptic feedback** — Tactile confirmation on every command button press
- **Adaptive layout** — Side-by-side panels on tablets/landscape, tabbed interface on phones

### Terminal
- **Colour-coded output** — Green (RX), blue (TX), yellow (system messages)
- **Line buffering** — Accumulates serial bytes until newline for clean line-by-line display
- **5,000-line buffer** — Auto-trims oldest lines to keep memory bounded
- **Timestamps** — Optional per-line timestamps (HH:MM:SS.mmm)
- **Log export** — Save terminal output to file
- **Wake/Sleep filtering** — Hidden from acknowledgment popups but visible in terminal

### Release Features
- **Splash screen** — GaiaCode branded launch with logo fade-in animation
- **Boot logging** — Logs app version, platform, OS version, and startup time
- **Permission flow** — Explains why Bluetooth/Location permissions are needed, with "Open Settings" fallback
- **About screen** — Version, device info, Bluetooth status, contact details, open-source licenses
- **Connection recovery** — 10-second data timeout warning, connection lost callback, auto-reconnect from saved settings
- **USB device recognition** — Android system dialog offers to open app when serial adapter is plugged in

## Supported Sensors

| Profile | Sensor | Key Commands |
|---------|--------|-------------|
| **θ Theta Pico** | Compact broadband | 4-axis select, 8 gain levels (Vel ×1–10 / Acc ×1–50), mass centering, calibration, ADC zero |
| **θ Theta Standard** | Full broadband | Axis select, mass control, low/high gain, short/long period |
| **Σ Sigma** | Strong motion accelerometer | 4 gain ranges (0.5g–4g), mass positioning, zero mass position |
| **α Alpha** | Vault sensor | Axis lock/unlock, calibration, parameter storage, short/long period |

### Auto-Detection

When you connect, the app sends a sign-on query (`?`) and identifies the sensor from the response:

| Response contains | Profile loaded |
|-------------------|---------------|
| `GAIA ALPHA` | α Alpha |
| `GAIA Theta` | θ Theta Standard |
| `GAIA Theta...Pico` | θ Theta Pico |
| `GAIA SIGMA` | Σ Sigma |

## Installation

### From APK (Android)

1. Download the latest APK from [Releases](https://github.com/GaiaCode/Mobile_Sensor_Terminal/releases)
2. Enable "Install from unknown sources" in Android settings
3. Install the APK
4. Grant Bluetooth and Location permissions when prompted

### From Source

See [Building](#building) below.

## Building

### Prerequisites

- [Flutter SDK](https://flutter.dev/docs/get-started/install) ≥ 3.0
- [Android Studio](https://developer.android.com/studio) with Android SDK 36+
- For iOS: Xcode 15+ (macOS only)
- **Windows:** Developer Mode must be enabled (Settings → Developer options → toggle On)

### Build Steps

```bash
# Clone the repository
git clone https://github.com/GaiaCode/Mobile_Sensor_Terminal.git
cd Mobile_Sensor_Terminal

# Install dependencies
flutter pub get

# Generate app icons (one-time)
dart run flutter_launcher_icons:main

# Build debug APK
flutter build apk --debug

# Build release APK (in-house beta, debug-signed)
flutter build apk --release

# Run on connected device/emulator
flutter run
```

The APK will be at `build/app/outputs/flutter-apk/app-release.apk`.

### Known Build Notes

| Issue | Fix |
|-------|-----|
| `flutter_bluetooth_serial` namespace error | Auto-fixed by `settings.gradle.kts` hook |
| `lStar` attr not found | compileSdk forced to 36 for all subprojects |
| R8 missing Play Core classes | Minification disabled for beta builds |
| Kotlin cache errors on Windows (D: vs C:) | Harmless warnings — build still succeeds |
| Symlink errors on Windows | Enable Developer Mode in Windows settings |

### Release Signing (Production)

For Play Store builds, create a keystore and `android/key.properties`:

```bash
keytool -genkey -v -keystore gaiacode-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias gaiacode
```

```properties
# android/key.properties
storePassword=YOUR_PASSWORD
keyPassword=YOUR_PASSWORD
keyAlias=gaiacode
storeFile=../../gaiacode-release.jks
```

⚠️ **Never commit** `gaiacode-release.jks` or `key.properties` to git.

## Usage

### Connecting to a Sensor

1. **Power on** your GaiaCode sensor
2. Open the app — splash screen appears, then Connection screen
3. **Grant permissions** when prompted (Bluetooth + Location)
4. Select **Bluetooth** or **USB** tab
5. Tap **Scan** to discover Bluetooth devices, or plug in a USB OTG serial adapter
6. Select your sensor from the list
7. Baud rate defaults to **9600** (change if needed)
8. Tap to connect → app sends `?` → auto-detects sensor → loads correct profile

### Sending Commands

1. The **Commands** tab shows colour-coded button groups for your detected sensor
2. Tap any button — the app:
   - Sends a wake signal (`\r\n`)
   - Waits 150ms for sensor to wake
   - Sends the command
   - Shows acknowledgment: "✅ All Axes selected"
3. Switch to **Terminal** tab to see raw serial data
4. Type custom commands in the input bar at the bottom
5. Tap ℹ️ in the toolbar to view the About screen

### Command Groups

| Group | Colour | Purpose |
|-------|--------|---------|
| 🔵 **Axis Select** | Dark Teal (`#1e5a7a`) | Choose target axis (All/N/E/Z) |
| 🟤 **Mass & Cal** | Dark Brown (`#8b5e3c`) | Mass centering, motor control, calibration |
| 🟣 **Gain Control** | Dark Purple (`#5e3d7a`) | Set velocity/acceleration gain levels |
| ⚫ **Advanced** | Dark Slate (`#4a5568`) | Period selection, parameter storage, system info |

### Tips

- **Landscape mode** on tablets shows commands and terminal side-by-side
- Enable **Timestamps** in settings (⚙️) to track response timing
- Use **Save Log** to export terminal output for analysis
- If the sensor is sleeping, the wake-before-send handles it automatically
- The app remembers your last connection for quick reconnect

## Command Reference

### θ Theta Pico

| Icon | Button | Command |
|------|--------|---------|
| ✦ | All Axes | `A` |
| ↕ | North/South | `N` |
| ↔ | East/West | `E` |
| ⬍ | Vertical | `Z` |
| ⊕ | Centre Mass | `C` |
| ⚖ | Show Mass | `M` |
| ◀ | Motor (-) | `<` |
| ▶ | Motor (+) | `>` |
| ◉ | Cal Enable ON | `I` |
| ○ | Cal Enable OFF | `K` |
| ⬤ | All Cal ON | `T` |
| ◯ | All Cal OFF | `R` |
| ① | Vel × 1 | `1V` |
| ② | Vel × 2 | `2V` |
| ④ | Vel × 4 | `4V` |
| ⑩ | Vel × 10 | `10V` |
| ❶ | Acc × 1 | `1A` |
| ❺ | Acc × 5 | `5A` |
| ❿ | Acc × 10 | `10A` |
| ㊿ | Acc × 50 | `50A` |
| ⏱ | Short (30s) | `S` |
| ⏲ | Mid (60s) | `L` |
| ⏳ | Long (120s) | `B` |
| ☰ | Show Params | `D` |
| 💾 | Store Params | `Q` |
| 📌 | Save ADC Zero | `9` |
| 📋 | Read ADC Zero | `%` |

### θ Theta Standard

| Icon | Button | Command |
|------|--------|---------|
| ✦ | All Axes | `A` |
| ↕ | North/South | `N` |
| ↔ | East/West | `E` |
| ⬍ | Vertical | `Z` |
| ⊕ | Centre Mass | `C` |
| ⚖ | Show Mass | `M` |
| ◀ | Motor (-) | `<` |
| ▶ | Motor (+) | `>` |
| ⊘ | Zero Mass Pos | `=` |
| ◉ | Cal Enable ON | `I` |
| ○ | Cal Enable OFF | `K` |
| ▽ | Low Gain | `G` |
| △ | High Gain | `H` |
| ℹ | Sign-On Msg | `?` |
| ⏱ | Short Period | `S` |
| ⏳ | Long Period | `B` |
| ☰ | Show Params | `D` |

### Σ Sigma

| Icon | Button | Command |
|------|--------|---------|
| ✦ | All Axes | `A` |
| ↕ | North/South | `N` |
| ↔ | East/West | `E` |
| ⬍ | Vertical | `Z` |
| ⊕ | Centre Mass | `C` |
| ⚖ | Show Mass | `M` |
| ◀ | Motor (-) | `<` |
| ▶ | Motor (+) | `>` |
| ⊘ | Zero Mass Pos | `=` |
| ▫ | 0.5g Gain | `1G` |
| ◻ | 1g Gain | `2G` |
| ◼ | 2g Gain | `3G` |
| ⬛ | 4g Gain | `4G` |
| ℹ | Sign-On Msg | `?` |
| ☰ | Show Params | `D` |

### α Alpha

| Icon | Button | Command |
|------|--------|---------|
| ✦ | All Axes | `A` |
| ↕ | North/South | `N` |
| ↔ | East/West | `E` |
| ⬍ | Vertical | `Z` |
| ⊕ | Centre Mass | `C` |
| ⚖ | Show Mass | `M` |
| ◀ | Motor (-) | `<` |
| ▶ | Motor (+) | `>` |
| ⊘ | Zero Mass Pos | `=` |
| ◉ | Cal Enable ON | `I` |
| ○ | Cal Enable OFF | `K` |
| ℹ | Sign-On Msg | `?` |
| ⏱ | Short Period | `S` |
| ⏳ | Long Period | `B` |
| ☰ | Show Params | `D` |
| 💾 | Store Params | `Q` |
| 🔒 | Lock Axes | `L` |
| 🔓 | Unlock Axes | `U` |

## Architecture

### Project Structure

```
Mobile_Sensor_Terminal/
├── pubspec.yaml                       # Dependencies + assets + icon config
├── analysis_options.yaml              # Lints
├── assets/
│   ├── Gaiacode.png                   # Branding (splash, about, connection)
│   └── logo.png                       # App icon source
├── android/
│   ├── app/
│   │   ├── build.gradle.kts           # compileSdk 36, signing config
│   │   ├── proguard-rules.pro         # Keep rules + Play Core dontwarn
│   │   └── src/main/
│   │       ├── AndroidManifest.xml    # BT + USB + location permissions
│   │       └── res/xml/
│   │           └── device_filter.xml  # USB vendor IDs (FTDI, CP210x, etc.)
│   ├── build.gradle.kts               # Repository config
│   └── settings.gradle.kts            # Namespace + compileSdk fixes for old plugins
└── lib/                               # 2,334 lines of Dart
    ├── main.dart                      # App entry, theme, boot logging
    ├── models/
    │   └── sensor_profiles.dart       # 4 profiles, icons, colours (219 lines)
    ├── screens/
    │   ├── splash_screen.dart         # Logo fade-in → connection (82 lines)
    │   ├── connection_screen.dart     # BT/USB scan, permissions (482 lines)
    │   ├── terminal_screen.dart       # Commands + terminal, adaptive (477 lines)
    │   └── about_screen.dart          # Version, device info (154 lines)
    ├── services/
    │   ├── serial_service.dart        # Abstract interface (29 lines)
    │   ├── bluetooth_serial_service.dart  # BT Classic + line buffer (128 lines)
    │   ├── usb_serial_service.dart    # USB OTG + line buffer (138 lines)
    │   └── connection_manager.dart    # Unified manager + recovery (173 lines)
    └── widgets/
        ├── command_grid.dart          # Responsive button grid (133 lines)
        ├── serial_monitor.dart        # Terminal display (225 lines)
        └── branding_header.dart       # Logo widget (35 lines)
```

### Data Flow

```
[Sensor] ←→ [Bluetooth/USB] ←→ [SerialService] ←→ [ConnectionManager]
                                      ↓                      ↓
                              [Line Buffer]          [SharedPreferences]
                                      ↓                (last connection)
                              [dataStream]
                                  ↓     ↓
                        [SerialMonitor] [TerminalScreen]
                        (terminal UI)   (ack + auto-detect)
```

### Serial Protocol

All GaiaCode sensors use the same basic protocol:
- **Baud rate:** 9600, 8N1
- **Line ending:** CR+LF (`\r\n`)
- **Sleep mode:** Sensor sleeps after inactivity; any character wakes it
- **Echo:** Commands are echoed (e.g., sending `C` returns `cCentre North`)
- **Sign-on:** `?` command returns sensor identification string starting with `GAIA`

### Supported USB Chipsets

The app recognises these USB-to-serial chipsets via `device_filter.xml`:

| Chipset | Vendor ID | Common in |
|---------|-----------|-----------|
| FTDI | 1027 | Professional serial adapters |
| Silicon Labs CP210x | 4292 | Development boards |
| Prolific PL2303 | 1659 | Budget serial cables |
| CH340/CH341 | 6790 | Arduino clones, cheap adapters |
| Arduino | 9025 | Arduino boards |
| Generic CDC ACM | 8137 | Standard USB serial |

## Permissions

| Permission | Purpose | When Requested |
|-----------|---------|----------------|
| `BLUETOOTH` | Bluetooth Classic communication | App launch |
| `BLUETOOTH_ADMIN` | Device discovery | App launch |
| `BLUETOOTH_SCAN` | Android 12+ scanning | App launch |
| `BLUETOOTH_CONNECT` | Android 12+ connections | App launch |
| `ACCESS_FINE_LOCATION` | Required for BT discovery (Android 6–11) | App launch |
| `USB_HOST` | USB OTG serial access | Automatic |

## Related Projects

- [Sensor Terminal (Desktop)](https://github.com/GaiaCode/Seismo-Tools) — Python/Tkinter desktop version
- [Zeta](https://github.com/GaiaCode/Zeta) — Desktop seismic workstation (Tauri/Rust)

## Contributing

Contributions welcome! Please see the [desktop project's CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <img src="assets/logo.png" alt="GaiaCode" width="48"/><br/>
  <strong>GaiaCode</strong><br/>
  <a href="https://www.gaiacode.com">www.gaiacode.com</a>
</p>
