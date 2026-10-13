import numpy as np
from scipy.signal import chirp
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 60
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t1 = np.linspace(0, 30, int(sampling_rate * 30), endpoint=False)
# 30s Dual Tone (2 Hz + 10 Hz)
part1 = 500.0 * np.sin(2 * np.pi * 2.0 * t1) + 300.0 * np.sin(2 * np.pi * 10.0 * t1)

t2 = np.linspace(0, 30, int(sampling_rate * 30), endpoint=False)
# 30s Chirp (1 Hz to 35 Hz)
part2 = 600.0 * chirp(t2, f0=1.0, f1=35.0, t1=30.0, method='linear')

data = np.concatenate([part1, part2]).astype(np.int32)

# Apply the same synthetic wavefield across all three components
header_z = {'network': 'XX', 'station': 'SYN04', 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time}
header_n = {'network': 'XX', 'station': 'SYN04', 'location': '00', 'channel': 'HHN', 'sampling_rate': sampling_rate, 'starttime': start_time}
header_e = {'network': 'XX', 'station': 'SYN04', 'location': '00', 'channel': 'HHE', 'sampling_rate': sampling_rate, 'starttime': start_time}

st = Stream(traces=[
    Trace(data=data, header=header_z),
    Trace(data=data, header=header_n),
    Trace(data=data, header=header_e)
])

st.write("synthetic_module4_spectra.mseed", format="MSEED")
print("Generated: synthetic_module4_spectra.mseed (3-Component)")
