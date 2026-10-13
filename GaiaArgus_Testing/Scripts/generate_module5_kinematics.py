import numpy as np
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 60
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

# 2 Hz Acceleration pulse between t=10s and t=12s
accel_pulse = np.zeros(npts)
idx_start = int(10 * sampling_rate)
idx_end = int(12 * sampling_rate)
t_pulse = t[idx_start:idx_end] - 10.0
accel_pulse[idx_start:idx_end] = 200.0 * np.sin(2 * np.pi * 2.0 * t_pulse)

# Add constant DC offset bias (15 counts)
data_z = accel_pulse + 15.0
data_n = (accel_pulse * 0.7) + 15.0
data_e = (accel_pulse * 0.4) + 15.0

channels = [('HHZ', data_z), ('HHN', data_n), ('HHE', data_e)]
traces = []
for ch, d in channels:
    hdr = {'network': 'XX', 'station': 'SYN05', 'location': '00', 'channel': ch, 'sampling_rate': sampling_rate, 'starttime': start_time}
    traces.append(Trace(data=d.astype(np.int32), header=hdr))

st = Stream(traces=traces)
st.write("synthetic_module5_kinematics.mseed", format="MSEED")
print("Generated: synthetic_module5_kinematics.mseed")
