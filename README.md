# Seismo Tools

A collection of utilities for seismology, sensor testing, and instrument control — desktop instrument panels, a mobile sensor terminal for GAIA sensors/digitizers, and a synthetic-data test suite for seismic signal-processing modules.

---

## Repository Contents

| Path | Description |
|------|-------------|
| `siggen_panel.py` + `siggen_panel.spec` | Signal generator control panel (VISA) |
| `dmm_panel.py` + `dmm_panel.spec` | Digital multimeter control panel (VISA) |
| `Sensor_Terminal.py` + `Sensor_Terminal.spec` | Serial sensor terminal with logging |
| `Sensor_Polarity_Check.py` | Sensor polarity verification tool (VISA) |
| `hardware.py` | Shared serial instrument controller (sig gen / DMM / aux) |
| `Mobile_Sensor_Terminal/` | Flutter mobile app — universal GAIA sensor terminal |
| `GaiaArgus_Testing/` | Synthetic-data generators + fixtures for seismic processing modules |

---

## 1. Desktop Instrument Panels (Python / tkinter)

All desktop tools share the GaiaCode MD3 dark UI theme and run on Windows or Linux.

### Signal Generator Panel — `siggen_panel.py`
Control panel for a bench signal/function generator over VISA: waveform selection, frequency/amplitude control, and output management for sensor calibration and receiver validation.

```bash
python siggen_panel.py
```

### DMM Panel — `dmm_panel.py`
Control and logging interface for a bench digital multimeter over VISA: voltage/current/resistance measurement, trend display, and timestamped logging.

```bash
python dmm_panel.py
```

### Sensor Terminal — `Sensor_Terminal.py`
Serial (COM/tty) sensor terminal for field testing: multi-channel readout, real-time monitoring, and data logging.

```bash
python Sensor_Terminal.py
```

### Sensor Polarity Check — `Sensor_Polarity_Check.py`
Guided polarity verification for installed sensors using the signal generator + DMM over VISA.

```bash
python Sensor_Polarity_Check.py
```

### Hardware Controller — `hardware.py`
Shared `InstrumentController` class used by the panels: opens/configures the signal generator, DMM, and AUX serial ports. Edit the `CONFIG` dict at the top of the file to match your COM ports and baud rates (defaults: `COM4`/`COM5`/`COM6` @ 9600).

### Standalone builds (PyInstaller)
```bash
pip install pyinstaller
pyinstaller siggen_panel.spec
pyinstaller dmm_panel.spec
pyinstaller Sensor_Terminal.spec
# Executables land in dist/
```

---

## 2. Mobile Sensor Terminal (Flutter)

`Mobile_Sensor_Terminal/` — **GaiaCode Universal Sensor Terminal (Mobile)**, a Flutter app (Android primary; iOS/macOS/Windows/Linux/web scaffolding included) for talking to GAIA-family sensors and digitizers in the field.

**Features:**
- Bluetooth Classic serial (`flutter_bluetooth_serial`) and USB OTG serial (`usb_serial`), behind a unified `ConnectionManager`
- Terminal screen with command send/response monitoring
- Predefined command sets for GAIA sensor variants (Theta / Alpha / Sigma) — see `Messages and responses*.txt`
- Serial monitor widgets, connection screen, splash/about screens

**Setup:**
```bash
cd Mobile_Sensor_Terminal
flutter pub get
flutter run            # attached device
flutter build apk      # Android package
```

For release signing, create `android/key.properties` as described in the app README and never commit real keystores or `key.properties` (both are gitignored).

---

## 3. GaiaArgus Testing Suite

`GaiaArgus_Testing/` — synthetic miniSEED fixtures and generator scripts for exercising the GaiaArgus / GaiaSignal seismic processing modules end-to-end without real station data.

**Generator scripts** (`GaiaArgus_Testing/Scripts/`, ObsPy-based):

| Script | Module under test |
|--------|-------------------|
| `generate_module1.py` | Data ingestion |
| `generate_modult2_gaps.py` | QC / gap detection |
| `generate_module3_helicorder.py` | Helicorder display |
| `generate_module4_spectra.py` | Fourier / response spectra |
| `generate_module5_kinematics.py` | Strong-motion kinematics (PGA/PGV/PGD, Arias) |
| `generate_module6_polarization.py`, `hodogram.py` | Polarization analysis / hodograms |
| `generate_module7_oma_fdd.py` | Operational modal analysis (FDD) |
| `generate_module8_hvsr.py` | HVSR (Nakamura) |
| `generate_module9_dvv.py`, `dvv.py`, `baseline.py` | dv/v monitoring (ambient noise) |
| `generate_module10_phase_hypodd.py` | Phase picking / hypoDD relocation inputs |
| `generate_module11_masw.py` | MASW surface-wave dispersion |

Synthetic waveforms are written to `GaiaArgus_Testing/Synthetic Data/` (miniSEED, `XX` test network, `SYNxx` station codes). Product manuals and module reference docs (`MODULES.md`, PDFs, HTML) are included in the same directory.

---

## Technology Stack

- **Python 3.8+** — tkinter GUIs, PyVISA (`pyvisa`), PySerial (`pyserial`), ObsPy / NumPy / SciPy (testing suite)
- **Flutter / Dart** (SDK >=3.0.0 <4.0.0) — mobile terminal app
- **PyInstaller** — standalone desktop builds

## Hardware Dependencies

- VISA-compatible bench signal generator and digital multimeter (desktop panels)
- Serial / USB sensors and digitizers (Sensor Terminal, `hardware.py`)
- GAIA-family seismic sensors/digitizers over Bluetooth Classic or USB OTG (mobile app)

## Data Formats & Protocols

- **miniSEED** — synthetic waveform fixtures (ObsPy `read`/`write`)
- **SCPI over VISA** — bench instrument control
- **Serial (UART / Bluetooth SPP / USB OTG)** — GAIA sensor command/response protocol (documented in `Mobile_Sensor_Terminal/Messages and responses*.txt`)

## Installation

```bash
# Desktop panels
pip install pyvisa pyvisa-py pyserial

# Testing suite
pip install obspy numpy scipy

# Mobile app
cd Mobile_Sensor_Terminal && flutter pub get
```

## License

See `LICENSE.md`. Contributions: `CONTRIBUTING.md`.
