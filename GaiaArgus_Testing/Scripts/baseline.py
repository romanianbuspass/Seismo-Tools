import numpy as np
from scipy.interpolate import interp1d
from obspy import Trace, Stream, UTCDateTime

def generate_test_blocks():
    fs = 100.0
    duration_sec = 300.0  # 5 minutes of noise
    t = np.arange(0, duration_sec, 1 / fs)

    # 1. Generate Baseline Coda
    np.random.seed(42)
    base_signal = np.random.normal(0, 1, len(t)) * np.exp(-t / 30.0)

    tr_base = Trace(data=(base_signal * 10000).astype(np.int32))
    tr_base.stats.network = 'XX'
    tr_base.stats.station = 'SYN21'
    tr_base.stats.channel = 'HHZ'
    tr_base.stats.sampling_rate = fs
    Stream([tr_base]).write("baseline.mseed", format="MSEED")

    # 2. Generate Anomaly Coda (-1.0% dv/v drop)
    stretch_factor = 1.0 - (-0.01) # Stretches the wave
    t_stretched = t * stretch_factor
    interpolator = interp1d(t, base_signal, bounds_error=False, fill_value=0.0)
    
    # Add minor uncorrelated noise so it isn't mathematically perfect
    anomaly_signal = interpolator(t_stretched) + np.random.normal(0, 0.1, len(t))

    tr_anom = Trace(data=(anomaly_signal * 10000).astype(np.int32))
    tr_anom.stats.network = 'XX'
    tr_anom.stats.station = 'SYN21'
    tr_anom.stats.channel = 'HHZ'
    tr_anom.stats.sampling_rate = fs
    Stream([tr_anom]).write("anomaly.mseed", format="MSEED")

    print("Created baseline_SYN21.mseed and anomaly_SYN21.mseed")

if __name__ == "__main__":
    generate_test_blocks()
