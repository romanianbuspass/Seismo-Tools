# GaiaSignal — Module & Tool Reference

Lightweight web-based seismic signal processing and streaming application.
Streamlit UI + ObsPy/SciPy/NumPy DSP in Python, with the hot-path DSP ported to a Rust PyO3 extension (`gaia_dsp`).

---

## Entry Points & Top-Level

| Path | Purpose |
|---|---|
| `app.py` | Streamlit multi-page dashboard: file upload, live SeedLink view, detrend/filter, integration & IMs, FAS/response spectra, RotD, HVSR, OMA tracking, PDF reports, traffic-light alarms. |
| `Makefile` | Shortcuts: `dev` (maturin develop), `build` (wheel), `test` (full parity suite), `bench`, `app`, `clean`. |
| `requirements.txt` | Python dependencies. |
| `Instructions.md` | Original autonomous-agent build spec (phases 1–N). |
| `Agent_Epics.md` | Feature epic backlog/planning notes. |

---

## `core/` — Python DSP Layer

| Module | Purpose |
|---|---|
| `io.py` | Data ingestion: `load_mseed` (via ObsPy) and `load_ascii` (single/multi-column `.txt`/`.dat`, unit auto-detection, 3C channel detection). |
| `preprocess.py` | Baseline correction (constant/linear/quadratic detrend) and 4th-order Butterworth filtering (HP/LP/BP, zero-phase), optional decimation, component lookup helpers. |
| `integration.py` | Acceleration→velocity/displacement integration plus intensity measures (PGA/PGV/PGD, Arias, CAV, etc.); dispatches to Rust when available. |
| `spectrum.py` | Fourier amplitude spectra, elastic SDOF response spectra, RotD100 spectra from horizontal pairs; Rust-accelerated with SciPy fallback. |
| `response.py` | Instrument response removal: StationXML inventory loading, sensitivity application, `polezero.ini` parsing, PZ-based deconvolution. |
| `oma.py` | Operational Modal Analysis tracker: Welch PSD, top-peak detection, SQLite logging of structural resonance history. |
| `alerts.py` | Traffic-light alarm evaluation against `config/alarms.yaml`; email alert hook (stub). |
| `reporting.py` | Branded PDF report generation (figures → PNG → report). |

## `streaming/` — Live Data

| Module | Purpose |
|---|---|
| `seedlink_client.py` | `SeedLinkClient` + `SeedLinkBuffer`: threaded SeedLink ingestion into a time-aware rolling ObsPy Stream buffer with gap/overlap handling. |

## `gaia_dsp/` — Rust PyO3 Extension

Compiled via maturin; exposes accelerated DSP to Python.

| Module | Purpose |
|---|---|
| `lib.rs` | Core bindings: Butterworth filtering, integration/IMs, FAS + Konno-Ohmachi smoothing, HVSR, STFT spectrogram, Welch PSD, elastic/inelastic (constant-ductility) response spectra, RotD, ring buffer, response removal. |
| `filter.rs` | IIR Butterworth filters + zero-phase filtfilt (biquad sections); seismic frequency-band selection. |
| `steim.rs` | Pure-Rust Steim1/Steim2 decoders (libmseed-compatible semantics). |
| `miniseed.rs` | Native miniSEED parser: FSDH, Blockette 1000, Steim payload routing. |
| `trigger.rs` | Recursive STA/LTA trigger for P-wave arrival detection. |
| `fk.rs` | Frequency-wavenumber (F-K) beamforming for array processing. |
| `interferometry.rs` | Ambient noise interferometry: cross-correlation workflow. |
| `masw.rs` | MASW surface-wave dispersion analysis. |
| `hypodd.rs` | Simplified HypoDD-style double-difference hypocenter relocation. |

## `solvers/` & `external_solvers/` — Location Codes

| Path | Purpose |
|---|---|
| `solvers/` | Prebuilt NonLinLoc Windows binaries (`NLLoc.exe`, `Grid2Time.exe`, `Vel2Grid.exe` + runtime dll). |
| `external_solvers/NonLinLoc/` | Full NonLinLoc source tree + `README_BUILD.md` (build notes). |

## `gaia-station-app/` — Tauri Desktop App ("Gaia-Argus")

Tauri v2 + SvelteKit + TypeScript desktop front-end. Rust backend (`src-tauri/src`): `commands.rs` (IPC), `config.rs`, `database.rs`, `export.rs`, `helicorder.rs`, `location.rs`, `hypodd.rs`, `interferometry.rs`, `local_io.rs`. Ships `docs/` with Operator/Admin guides and the compiled `Gaia-Argus_Manual.pdf` (build via `npm run docs:build`).

## `scripts/` — Deployment

| Script | Purpose |
|---|---|
| `build_windows_wheel.bat` / `.sh` | Build the Windows wheel natively / cross-compile from Linux. |
| `install_windows_wheel.bat` | Install the wheel on Windows. |
| `install_service.bat` / `uninstall_service.bat` | Register/remove GaiaSignal as an NSSM Windows service. |

## Standalone Diagnostic Tools

| Tool | Purpose |
|---|---|
| `tau_stream_debug.py` | GAIA TAU SeedLink baseline validator (raw-socket uni-station handshake, 520-byte frames, continuity/gap stats) — Linux. |
| `tau_stream_debug_win.py` | Same validator packaged for Windows CMD (wall-clock arrival timing, clean 60 s summary). |

## `config/`, `Data/`, `assets/`, `tests/`

| Path | Purpose |
|---|---|
| `config/alarms.yaml` | Traffic-light threshold configuration. |
| `Data/` | Sample data: accelerograms (SeismoSignal `.dat`), Event/Noise miniSEED, `XX.T743.xml` StationXML, `polezero.ini`. |
| `assets/` | Brand assets (GaiaCode icon, Encardio logo). |
| `tests/` | Parity/validation suite: Rust-vs-SciPy drift, integration, spectra, RotD, ring buffer, response removal, SeedLink buffer, 3C processing, accelerogram loading + `bench_dsp.py` benchmark. |
