import numpy as np
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 7200  # 2 hours
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

# Background ambient noise
data = np.random.normal(0, 50, npts)

# Function to add synthetic impulsive earthquake
def add_event(t_start_sec, amplitude):
    idx_start = int(t_start_sec * sampling_rate)
    length = int(30 * sampling_rate)  # 30-second duration
    t_event = np.linspace(0, 30, length)
    envelope = np.exp(-0.2 * t_event)
    signal = amplitude * np.sin(2 * np.pi * 4.0 * t_event) * envelope
    data[idx_start:idx_start+length] += signal

# Add events at 15m, 45m, and 1h 30m
add_event(900, 3000.0)   # 15 minutes
add_event(2700, 8000.0)  # 45 minutes (Large Event)
add_event(5400, 2500.0)  # 90 minutes

header = {'network': 'XX', 'station': 'SYN03', 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time}
st = Stream(traces=[Trace(data=data.astype(np.int32), header=header)])
st.write("synthetic_module3_helicorder.mseed", format="MSEED")
print("Generated: synthetic_module3_helicorder.mseed")
