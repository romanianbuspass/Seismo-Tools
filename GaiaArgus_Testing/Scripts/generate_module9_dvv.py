import numpy as np
from obspy import Trace, Stream, UTCDateTime

sampling_rate = 100.0
duration_sec = 3600  # 1 hour
npts = int(sampling_rate * duration_sec)
start_time = UTCDateTime("2026-08-01T00:00:00")

t = np.linspace(0, duration_sec, npts, endpoint=False)

# Common coherent noise source propagating between stations
coherent_noise = np.random.normal(0, 100, npts)

# File 1: Reference Stack (Station A & Station B)
stna_ref = coherent_noise + np.random.normal(0, 20, npts)
stnb_ref = np.roll(coherent_noise, 50) + np.random.normal(0, 20, npts)  # 0.5s baseline lag

hdr_a = {'network': 'XX', 'station': 'STNA', 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time}
hdr_b = {'network': 'XX', 'station': 'STNB', 'location': '00', 'channel': 'HHZ', 'sampling_rate': sampling_rate, 'starttime': start_time}

st_ref = Stream(traces=[Trace(data=stna_ref.astype(np.int32), header=hdr_a), Trace(data=stnb_ref.astype(np.int32), header=hdr_b)])
st_ref.write("synthetic_module9_ref.mseed", format="MSEED")

# File 2: Shifted Measurement (Introduce additional 2-sample delay to simulate dv/v change)
stnb_shifted = np.roll(coherent_noise, 52) + np.random.normal(0, 20, npts)
st_shifted = Stream(traces=[Trace(data=stna_ref.astype(np.int32), header=hdr_a), Trace(data=stnb_shifted.astype(np.int32), header=hdr_b)])
st_shifted.write("synthetic_module9_shifted.mseed", format="MSEED")

print("Generated: synthetic_module9_ref.mseed & synthetic_module9_shifted.mseed")
