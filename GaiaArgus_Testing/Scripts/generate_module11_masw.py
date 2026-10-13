import numpy as np
from scipy.signal import chirp
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 5
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)
num_channels = 12
receiver_spacing_m = 2.0

traces = []
for i in range(num_channels):
    distance = (i + 1) * receiver_spacing_m
    # Simulate dispersive arrival delay: low frequencies travel slower
    delay_sec = distance / 250.0  # nominal 250 m/s phase velocity
    
    data = np.zeros(npts)
    idx_start = int(delay_sec * sampling_rate)
    t_sweep = t[:npts-idx_start]
    
    # Dispersive chirp pulse
    sweep = 1000.0 * chirp(t_sweep, f0=30.0, f1=5.0, t1=1.5, method='linear') * np.exp(-2.0 * t_sweep)
    data[idx_start:] = sweep
    
    ch_name = f"CH{i+1:02d}"
    hdr = {'network': 'XX', 'station': 'MASW', 'location': '00', 'channel': ch_name, 'sampling_rate': sampling_rate, 'starttime': start_time}
    traces.append(Trace(data=data.astype(np.int32), header=hdr))

st = Stream(traces=traces)
st.write("synthetic_module11_masw.mseed", format="MSEED")
print("Generated: synthetic_module11_masw.mseed")
