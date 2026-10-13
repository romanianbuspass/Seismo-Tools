import numpy as np
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
start_time = UTCDateTime("2026-08-01T00:00:00")

# Segment 1: 0 to 25 seconds
t1 = np.linspace(0, 25, int(sampling_rate * 25), endpoint=False)
data1_z = (500 * np.sin(2 * np.pi * 2 * t1)).astype(np.int32)

# Segment 2: 30 to 60 seconds (5-second gap between 25s and 30s)
t2 = np.linspace(30, 60, int(sampling_rate * 30), endpoint=False)
data2_z = (500 * np.sin(2 * np.pi * 2 * t2)).astype(np.int32)

header1 = {'network': 'XX', 'station': 'SYN02', 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time}
header2 = {'network': 'XX', 'station': 'SYN02', 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time + 30.0}

tr1 = Trace(data=data1_z, header=header1)
tr2 = Trace(data=data2_z, header=header2)

st = Stream(traces=[tr1, tr2])
st.write("synthetic_module2_qc_gaps.mseed", format="MSEED")
print("Generated: synthetic_module2_qc_gaps.mseed")
