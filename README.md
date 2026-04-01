# IoT Time-Series Compression Pipeline

## Project Objective
In industrial IoT and edge-computing networks, continuous time-series sensors (like temperature, pressure, or vibrations) generate vast amounts of data. Transmitting this raw telemetry to the cloud in real-time drains both network bandwidth and battery life.

This project implements a highly efficient, hybrid **embedded-ready** compression pipeline that evaluates sensors stream point-by-point. It drastically reduces transmission overhead by smartly identifying and dropping redundant or highly predictable sensor readings—while guaranteeing a mathematically bounded limit on any absolute data accuracy lost.

---

## Algorithms Used

Our pipeline orchestrates three distinct mathematical approaches working iteratively in a continuous feedback loop:

1. **Adaptive Thresholding:** Continuously calculates a rolling sample standard deviation across the signal's volatility. It outputs a dynamic error bound ($\epsilon$). This prevents the system from locking up during chaotic sensor swings or clamping to zero during flat periods.
2. **Swinging Door Trending (SDT) (Lossy):** A lightning-fast geometric compression technique evaluating absolute temperature inputs. SDT calculates expanding "doors" based on the adaptive bounds. It will strictly drop data points until the physical linear trend breaks out of the allowable error window, at which point it securely marks an anchor.
3. **Delta Encoding (Lossless):** To optimize the network packet payload across the radio, the algorithm transmits only the relative delta changes mapped specifically between the surviving SDT anchors.

---

## Hardware Simulation Architecture

Designed strictly for easy porting natively to **C++ Arduino/Espressif microcontrollers**, the core framework utilizes a stateful `StreamCompressor` that completely bypasses rigid batch array (`numpy`) dependencies. 
It processes inputs sequentially matching standard `void loop()` architectures natively requiring $O(1)$ constant memory locally on the hardware via circular buffering.

### Execution Workflow

1. **Hardware Polling:** Generates or reads absolute IoT temperature samples one sequentially at a time.
2. **Volatility Analysis:** Temporarily measures point-by-point deltas purely to recalculate the dynamic $k$ stringency threshold limits.
3. **SDT Bounding:** Feeds the reading through the continuous Swinging Door geometric boundaries calculating maximum absolute error ceilings.
4. **Trigger & Transmit:** When bounds collapse, the radio is explicitly triggered to dispatch the relative Delta mapped from the previous transmission. 
5. **Reconstruction (Cloud Receiver):** At the backend server, the sparse packets are natively Delta-Decoded back into absolute Anchor coordinates, and the massive data gaps seamlessly bridged backwards over the timeframe natively utilizing either `linear` or Zero-Order Hold `step` interpolation.

---

## How to Run

Ensure you have activated your Python environment (Python 3.8+ recommended).

1. Clone or navigate into the repository:
   ```bash
   cd iot-compression
   ```
2. Install the necessary mathematical dependencies natively required for plotting:
   ```bash
   pip install numpy matplotlib
   ```

### 1. Hardware Stream Simulator
Quickly test the serial execution loop mathematically simulating raw edge node C++ behavior natively in terminal without overhead:
```bash
python simulate_arduino.py
```

### 2. Analytical Evaluation Suite
Run the full visualization suite actively capturing RMSE, network savings limits, and interactive `matplotlib` charts:
```bash
python main.py
```

---

## Example Outputs

Running the hardware pipeline dynamically generates console metrics natively representing transmission ratios:

```text
--- CLOUD RECEIVER DECODING ---
Total Cloud Packets Received: 26 (out of 1000 raw generated points)
Network Over-The-Air Reduction: 38.46x Ratio

Mathematical Drift Evaluation:
   Root Mean Square Error (RMSE): 1.1520 C
   [SUCCESS] Reconstructed signal strictly approximated original trajectory.
       
Arduino hardware streaming loop integration tested successfully.
```
*(By actively sweeping the core multiplier metric $\mathbf{k}$, you smoothly evaluate explicitly how lossy approximations securely trade structural signal fidelity flawlessly natively against massive local hardware battery savings!)*
