import numpy as np
from obspy import Trace, Stream, UTCDateTime

# Signal Parameters
sampling_rate = 100.0  # Hz
duration_sec = 60      # seconds
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

# 1. Channel Z: 1 Hz Sine + DC Offset
data_z = 1000.0 * np.sin(2 * np.pi * 1.0 * t) + 50.0

# 2. Channel N: 5 Hz Sine
data_n = 500.0 * np.sin(2 * np.pi * 5.0 * t)

# 3. Channel E: 10 Hz Sine
data_e = 250.0 * np.sin(2 * np.pi * 10.0 * t)

# Build ObsPy Traces
header_z = {'network': 'XX', 'station': 'SYN01', 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time}
header_n = {'network': 'XX', 'station': 'SYN01', 'location': '00', 'channel': 'HHN', 'sampling_rate': sampling_rate, 'starttime': start_time}
header_e = {'network': 'XX', 'station': 'SYN01', 'location': '00', 'channel': 'HHE', 'sampling_rate': sampling_rate, 'starttime': start_time}

st = Stream(traces=[
    Trace(data=data_z.astype(np.int32), header=header_z),
    Trace(data=data_n.astype(np.int32), header=header_n),
    Trace(data=data_e.astype(np.int32), header=header_e)
])

# Export miniSEED
output_filename = "synthetic_module1_ingestion.mseed"
st.write(output_filename, format="MSEED")
print(f"File successfully created: {output_filename}")
