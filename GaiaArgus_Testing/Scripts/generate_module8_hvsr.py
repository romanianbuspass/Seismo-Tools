import numpy as np
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 300  # 5 minutes
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

# Baseline noise
z = np.random.normal(0, 50, npts)
n = np.random.normal(0, 50, npts)
e = np.random.normal(0, 50, npts)

# Inject 3.0 Hz site resonance into horizontal components only
resonance_h = 250.0 * np.sin(2 * np.pi * 3.0 * t)
n += resonance_h
e += resonance_h

channels = [('HHZ', z), ('HHN', n), ('HHE', e)]
traces = []
for ch, d in channels:
    hdr = {'network': 'XX', 'station': 'SYN08', 'location': '00', 'channel': ch, 'sampling_rate': sampling_rate, 'starttime': start_time}
    traces.append(Trace(data=d.astype(np.int32), header=hdr))

st = Stream(traces=traces)
st.write("synthetic_module8_hvsr.mseed", format="MSEED")
print("Generated: synthetic_module8_hvsr.mseed")
