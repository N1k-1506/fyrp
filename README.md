# Stateful IoT Data Compression Pipeline

A cloud-based real-time telemetry processing pipeline designed to seamlessly compress continuous hardware sensor readings. This architecture natively evaluates edge-node inputs (e.g. from an ESP8266 or Arduino module) point-by-point, dynamically isolating mapping constraints to reduce sheer bandwidth payloads via the Swinging Door Trending (SDT) algorithmic concept.

## Architectural Overview

This system fundamentally operates across two networked boundaries utilizing standard HTTP over Wi-Fi:

### 1. The Edge Node (`arduino_port/arduino_sender`)
The physical hardware C++ codebase actively emulating an isolated real-world sensor node.
- Modifies and manages `timerDelay` constraints (default: 5.0 seconds).
- Dynamically validates incoming analog sensor readings to ensure integrity (`!isnan()`).
- Constructs raw JSON payloads (`{"value": 2x.xx}`) and transmits them blindly to the cloud gateway endpoint via POST.

### 2. The Cloud Gateway Server (`flask_server.py`)
A continuous Python processing endpoint running natively on the host workstation. 
- Serves as an active daemon thread listening on port 5000 (`/data`).
  - Pipes sequential points arriving from physical hardware through the active local `StreamCompressor`.
  - Mathematically evaluates if a point violates stateful standard error variance, triggering either an active mapping confirmation or a bandwidth-saving drop.

---

## Core Compression Algorithms

This repository implements lightweight, stateful time-series compression algorithms specifically tailored for constrained IoT memory pipelines:

- **Swinging Door Trending (SDT)** (`sdt.py`): A linear trend-filtering algorithm that isolates points acting as "anchors". It dynamically forms upper and lower doors based on acceptable data variances (`k * epsilon`). If a reading breaks the door's geometry, the previous point is transmitted.
- **Delta Encoding** (`delta.py`): Maps values strictly as differences (deltas) from the previous state rather than sending absolute integers/floats, drastically reducing byte sizes.
- **Adaptive Thresholding** (`adaptive.py`): Measures live signal volatility to actively shrink or expand the acceptable error threshold (Epsilon) during runtime.
- **Stateful Stream Wrapper** (`streaming.py`): Acts as the interface framework, allowing these algorithms to evaluate incoming HTTP arrays point-by-point indefinitely without ever overflowing RAM limits.

---

## Capabilities & Visualizations

### 1. Live GUI Telemetry Dashboard
Because real-time visualizations dictate absolute ownership over the python main-thread, the HTTP gateway parses inputs dynamically *behind* a secondary locking interface. When active data is intercepted, a Matplotlib display populates showing exactly what inputs have been filtered and dropped versus retained parameters. 

### 2. Stream Metrics Post-Mortem
The server implements a passive inactivity watcher. Once exactly 20 seconds of silence is registered, it automatically halts the visualization GUI, interprets it as a stream death, and runs the following exact state-evaluators:
- **Data Reduction Ratio (DRR)**: Evaluates exactly what percentage of the system bandwidth was formally saved.
- **Root Mean Square Error (RMSE)**: Calculates the numerical deviation of the lossy cloud reconstruction against the physical real-world inputs.

---

## Deployment & Execution

### Prerequisites
- Python 3.10+
- `pip install flask numpy matplotlib`
- Arduino IDE (configured with `ESP8266` board mapping files).

### Execution Steps

**1. Live Hardware Mode (ESP8266 Data Streaming)**
The primary application utilizes `flask_server.py` to actively ingest data directly from hardware.
1. Launch the Cloud Server listening sequence:
   ```bash
   python flask_server.py
   ```
2. Navigate into `arduino_port/arduino_sender/` and modify `arduino_sender.ino`. Ensure the network bounds (`ssid`, `password`, `serverUrl`) precisely correlate to your laptop. Note: use double backslashes `\\` for passwords containing explicit escape codes.
3. Push the firmware to your ESP8266 via USB matching 115200 serial baud routing.
4. Active data visualizations map identically as the network binds to the cloud ingestion sequence!

**2. Offline Simulation Mode (Testing only)**
If you wish to test the compression algorithms locally without any physical hardware, run the simulation daemon:
```bash
python main.py
```
