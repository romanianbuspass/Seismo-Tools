# Changelog

All notable changes to Seismo Tools are documented here.

## [Unreleased]

### Sensor Terminal
- [ ] Real-time FFT analysis
- [ ] Alarm notification system
- [ ] Multi-file batch logging
- [ ] Dark mode UI

### Signal Generator
- [ ] Frequency sweep (chirp) mode
- [ ] Harmonic series generation
- [ ] Amplitude modulation
- [ ] Hardware trigger support

### DMM Panel
- [ ] Multi-meter simultaneous logging
- [ ] Data export to HDF5
- [ ] Trend analysis & statistics
- [ ] Auto-ranging optimization

### Hardware Layer
- [ ] CAN bus support
- [ ] PWM frequency measurement
- [ ] Temperature sensor abstraction

---

## [1.0.0] – 12 Mar 2026

### Sensor Terminal
**Added:**
- ✅ Multi-channel data acquisition
- ✅ Real-time plotting
- ✅ CSV data export
- ✅ Configuration save/restore
- ✅ Temperature compensation
- ✅ Alarm thresholds
- ✅ Serial/USB device detection

### Signal Generator Panel
**Added:**
- ✅ Sine, square, triangle, sawtooth waveforms
- ✅ Frequency range 0.1 Hz – 10 kHz
- ✅ Amplitude & duty cycle control
- ✅ Real-time waveform preview
- ✅ CSV export for generated data
- ✅ Hardware DAC/GPIO integration

### DMM Panel
**Added:**
- ✅ Voltage/current/resistance measurement
- ✅ Real-time data logging
- ✅ USB/Serial device communication
- ✅ Auto-ranging support
- ✅ Unit conversion
- ✅ Trend visualization

### Hardware Interface
**Added:**
- ✅ GPIO control abstraction
- ✅ I2C device communication
- ✅ SPI support
- ✅ ADC/DAC abstraction
- ✅ Device enumeration
- ✅ Cross-platform support (Windows, Linux, Pi)

### Build System
**Added:**
- ✅ PyInstaller specs for standalone executables
- ✅ .gitignore for Python projects
- ✅ README & documentation

---

## Version History

### 0.5.0 – Alpha
- Initial prototypes
- Core functionality

---

## Known Issues

- Sensor Terminal: Serial latency >10ms on high baud rates
- Signal Generator: Frequency limits depend on DAC capability
- DMM Panel: Some multimeters require manual protocol configuration
- Hardware Layer: Raspberry Pi GPIO timing not deterministic

## Migration Guide

### Upgrading to 1.0.0
- No breaking changes (first release)
- All tools are compatible with Python 3.8+
- Database/config files: None (tools are stateless)

---

**Maintainer:** GaiaCode Engineering  
**Repository:** [github.com/gaiacode/seismo-tools]

For releases & downloads: [GitHub Releases]
