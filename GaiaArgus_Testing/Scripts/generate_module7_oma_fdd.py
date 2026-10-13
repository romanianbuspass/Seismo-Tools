import numpy as np
from scipy.signal import butter, filtfilt
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 120
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

# Shared structural modal resonances
mode1 = 400.0 * np.sin(2 * np.pi * 2.5 * t)  # 2.5 Hz Primary Mode
mode2 = 150.0 * np.sin(2 * np.pi * 7.0 * t)  # 7.0 Hz Secondary Mode

stations = ['ST01', 'ST02', 'ST03', 'ST04']
traces = []

for i, stn in enumerate(stations):
    # Mode shape amplitudes vary by station (sensor position)
    amp_factor = (i + 1) * 0.25
    noise = np.random.normal(0, 30, npts)
    signal = (mode1 * amp_factor) + (mode2 * (1.0 - amp_factor)) + noise
    
    hdr = {'network': 'XX', 'station': stn, 'location': '00', 'channel': 'HNZ', 'sampling_rate': sampling_rate, 'starttime': start_time}
    traces.append(Trace(data=signal.astype(np.int32), header=hdr))

st = Stream(traces=traces)
st.write("synthetic_module7_oma_fdd.mseed", format="MSEED")
print("Generated: synthetic_module7_oma_fdd.mseed")
