import numpy as np
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 60
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

# Noise baseline
z = np.random.normal(0, 10, npts)
n = np.random.normal(0, 10, npts)
e = np.random.normal(0, 10, npts)

# Add highly linear P-wave at t=20s along 45 degree back-azimuth
idx_start = int(20 * sampling_rate)
idx_end = int(25 * sampling_rate)
t_wave = t[idx_start:idx_end] - 20.0
p_signal = 1500.0 * np.sin(2 * np.pi * 3.0 * t_wave) * np.exp(-0.8 * t_wave)

azimuth_rad = np.radians(45.0)
z[idx_start:idx_end] += p_signal * 0.8
n[idx_start:idx_end] += p_signal * np.cos(azimuth_rad)
e[idx_start:idx_end] += p_signal * np.sin(azimuth_rad)

channels = [('HHZ', z), ('HHN', n), ('HHE', e)]
traces = []
for ch, d in channels:
    hdr = {'network': 'XX', 'station': 'SYN06', 'location': '00', 'channel': ch, 'sampling_rate': sampling_rate, 'starttime': start_time}
    traces.append(Trace(data=d.astype(np.int32), header=hdr))

st = Stream(traces=traces)
st.write("synthetic_module6_polarization.mseed", format="MSEED")
print("Generated: synthetic_module6_polarization.mseed")
