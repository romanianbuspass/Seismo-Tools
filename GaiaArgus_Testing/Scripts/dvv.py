import numpy as np
from scipy.interpolate import interp1d
from obspy import Trace, Stream, UTCDateTime

def generate_dvv_history():
    fs = 100.0
    duration_sec = 120.0  # 2 minutes of "stacked" noise per day
    t = np.arange(0, duration_sec, 1 / fs)
    
    # 1. Create a base "Green's Function" signature (a complex, decaying coda)
    # We use a fixed seed so the base scatterer pattern remains identical
    np.random.seed(42)
    base_noise = np.random.normal(0, 1, len(t))
    # Apply an exponential decay envelope to simulate natural coda wave dissipation
    base_signal = base_noise * np.exp(-t / 20.0)
    
    traces = []
    # Start at midnight on the 1st of the month
    start_date = UTCDateTime("2026-08-01T00:00:00")
    
    print("Generating 30-day Ambient Noise history...")
    
    for day in range(30):
        # 2. Inject a -1.0% velocity drop (dv/v) between Day 10 and Day 20
        if 10 <= day <= 20:
            dv_v = -0.01 
        else:
            dv_v = 0.0
            
        # In Coda Wave Interferometry, a velocity drop results in time stretching.
        # dt = -t * (dv/v) -> t_new = t * (1 - dv/v)
        stretch_factor = 1.0 - dv_v 
        t_stretched = t * stretch_factor
        
        # 3. Resample the base signal to the new stretched time axis
        interpolator = interp1d(t, base_signal, bounds_error=False, fill_value=0.0)
        daily_signal = interpolator(t_stretched)
        
        # 4. Inject a small amount of random daily uncorrelated noise (10% SNR) 
        # to ensure the backend's correlation algorithm has to work for it.
        daily_signal += np.random.normal(0, 0.1, len(t))
        
        # Scale to standard int32 counts
        final_counts = (daily_signal * 10000).astype(np.int32)
        
        # Fast-forward the timestamp by 24 hours per iteration
        trace_time = start_date + (day * 86400)
        
        hdr = {
            'network': 'XX',
            'station': 'SYN21',
            'location': '00',
            'channel': 'HHZ',
            'sampling_rate': fs,
            'starttime': trace_time
        }
        
        traces.append(Trace(data=final_counts, header=hdr))
        print(f"Computed Day {day+1:02d} ... dv/v applied: {dv_v*100:.1f}%")
        
    st = Stream(traces=traces)
    filename = "synthetic_module10_ambient_SYN21.mseed"
    st.write(filename, format="MSEED")
    print(f"\nSuccessfully wrote: {filename}")

if __name__ == "__main__":
    generate_dvv_history()
