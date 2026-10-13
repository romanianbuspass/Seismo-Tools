import numpy as np
from obspy import Trace, Stream, UTCDateTime

# Native NumPy implementation of the Ricker wavelet to bypass SciPy dependencies
def ricker(points, a):
    A = 2 / (np.sqrt(3 * a) * (np.pi**0.25))
    vec = np.arange(0, points) - (points - 1.0) / 2
    xsq = vec**2
    wsq = a**2
    return A * (1 - xsq / wsq) * np.exp(-xsq / (2 * wsq))

sampling_rate = 100.0
duration_sec = 60
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

stations = [
    ('STN01', 10.0, 15.0), # (Station ID, P_arrival_sec, S_arrival_sec)
    ('STN02', 12.5, 19.0),
    ('STN03', 15.0, 23.0),
]

traces = []
p_wavelet = ricker(200, 4.0) * 1000.0
s_wavelet = ricker(300, 2.0) * 2000.0

for stn, p_time, s_time in stations:
    data_z = np.random.normal(0, 10, npts)
    data_n = np.random.normal(0, 10, npts)
    
    # Inject P-wave on Z component
    p_idx = int(p_time * sampling_rate)
    data_z[p_idx:p_idx+len(p_wavelet)] += p_wavelet
    
    # Inject S-wave on N component
    s_idx = int(s_time * sampling_rate)
    data_n[s_idx:s_idx+len(s_wavelet)] += s_wavelet
    
    hdr_z = {'network': 'XX', 'station': stn, 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time}
    hdr_n = {'network': 'XX', 'station': stn, 'location': '00', 'channel': 'HHN', 'sampling_rate': sampling_rate, 'starttime': start_time}
    
    traces.append(Trace(data=data_z.astype(np.int32), header=hdr_z))
    traces.append(Trace(data=data_n.astype(np.int32), header=hdr_n))

st = Stream(traces=traces)
st.write("synthetic_module10_events.mseed", format="MSEED")
print("Generated: synthetic_module10_events.mseed")
