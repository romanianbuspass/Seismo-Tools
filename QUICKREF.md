# Quick Reference – Seismo Tools

## Installation

```bash
pip install PyQt5 pyserial numpy matplotlib
```

## Running Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Sensor Terminal | `python Sensor_Terminal.py` | Multi-sensor data logging |
| Signal Generator | `python siggen_panel.py` | Waveform synthesis |
| DMM Panel | `python dmm_panel.py` | Multimeter control |

## Building Executables

```bash
pip install pyinstaller
pyinstaller Sensor_Terminal.spec
pyinstaller siggen_panel.spec
pyinstaller dmm_panel.spec
# Output: dist/Sensor_Terminal/, dist/siggen_panel/, dist/dmm_panel/
```

## Sensor Terminal API

```python
from Sensor_Terminal import SensorTerminal

app = SensorTerminal()
app.start_logging()
app.add_channel("Temperature", unit="°C")
app.read_all()
app.stop_logging()
```

## Signal Generator Waveforms

| Type | Frequency Range | Example |
|------|-----------------|---------|
| Sine | 0.1 Hz – 10 kHz | 1 kHz, 1V amplitude |
| Square | 0.1 Hz – 5 kHz | 100 Hz, 50% duty |
| Triangle | 0.1 Hz – 5 kHz | 500 Hz, symmetric |
| Sawtooth | 0.1 Hz – 5 kHz | 100 Hz, variable duty |

## Hardware Layer (hardware.py)

```python
from hardware import GPIO, I2C, ADC, DAC

# GPIO control
gpio = GPIO()
gpio.set_pin(17, True)
gpio.set_pin(27, False)

# I2C sensors
i2c = I2C(address=0x48)
value = i2c.read(register=0x01)

# Analog I/O
adc = ADC(channel=0)
raw = adc.read()  # 0-4095 (12-bit)

dac = DAC(channel=1)
dac.write(2048)  # Set 50% output
```

## Serial Port Detection

```bash
# List available ports
python -m serial.tools.list_ports

# Test connection
python -c "import serial; s = serial.Serial('COM3', 115200); print(s.name)"
```

## Data Export Formats

**CSV (Sensor Terminal):**
```
Timestamp,Channel_1,Channel_2
2026-03-12T10:30:45.123,23.45,1234
```

**Signal Generator:**
```
Time(s),Amplitude
0.000,0.0
0.001,0.123
```

## Troubleshooting

### Serial Port Issues
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER

# Windows: Check Device Manager for COM port
```

### Missing Dependencies
```bash
pip install PyQt5 pyserial numpy matplotlib
```

### Build Standalone EXE
```bash
pyinstaller --onefile Sensor_Terminal.py
```

---

**Last Updated:** 12 Mar 2026
