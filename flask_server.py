import threading
import time
import sys
import numpy as np
from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from algorithms.streaming import StreamCompressor
from algorithms.reconstruction import reconstruct_signal
from metrics.evaluation import calculate_drr, calculate_rmse
from visualization.plots import plot_reconstruction, plot_transmitted_points

# Suppress Werkzeug default HTTP request logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Shared Multi-threaded Data Locks
data_lock = threading.Lock()
MAX_POINTS = 100 # Visual GUI buffer constraint per new requirements

raw_times = []
raw_values = []
comp_times = []
comp_values = []

# Persistent arrays mapping historical stream values for final computations
full_raw_times = []
full_raw_values = []
full_comp_times = []
full_comp_values = []

# Global compressor and system state trackers
compressor = StreamCompressor(window_size=10, k=2.5, debug=False)
system_tick = 0
last_received_time = 0.0
timeout_triggered = False

@app.route('/data', methods=['POST'])
def receive_data():
    global system_tick, last_received_time
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({"error": "No value provided in JSON payload"}), 400

        current_temp = float(data['value'])
        
        # Output raw incoming metric for shell observability
        print(f"[RECEIVE] Raw Hardware Read -> Temp: {current_temp:.2f} C")

        with data_lock:
            # Refresh inactivity detection bounds
            last_received_time = time.time()
            
            current_tick = system_tick
            system_tick += 1
            
            # Map point sequentially to memory compressor core
            should_transmit, payload = compressor.process_data_point(current_temp)

            raw_times.append(current_tick)
            raw_values.append(current_temp)
            
            full_raw_times.append(current_tick)
            full_raw_values.append(current_temp)
            
            # Maintain active memory constraint for GUI optimization
            if len(raw_times) > MAX_POINTS:
                raw_times.pop(0)
                raw_values.pop(0)

            # Route compression payload state
            if should_transmit:
                t, delta_val = payload
                
                comp_times.append(t)
                comp_values.append(current_temp)
                
                full_comp_times.append(t)
                full_comp_values.append(current_temp)
                full_comp_deltas.append(delta_val)
                
                # Keep sliding window clean
                while comp_times and comp_times[0] < raw_times[0]:
                    comp_times.pop(0)
                    comp_values.pop(0)

                print(f"[TX TRIGGERED] Timestamp: {t:03d} | Delta Payload: {delta_val:+.4f} | Absolute Temp: {current_temp:.2f} C")
                return jsonify({"status": "success", "transmitted": True, "timestamp": t, "delta": delta_val}), 200
            else:
                return jsonify({"status": "success", "transmitted": False}), 200

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

def run_flask():
    """Runs the flask server in a background thread."""
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def monitor_timeout():
    """Background monitor thread to track streaming inactivity intervals."""
    global timeout_triggered
    while True:
        time.sleep(1)
        # Requirement trigger: 20-second timeout event handles metric finalization
        if last_received_time > 0 and (time.time() - last_received_time) > 20.0:
            print("\n[TIMEOUT] 20-second inactivity limit triggered.")
            print("Processing final payload metric sequence...\n")
            timeout_triggered = True
            break

# Data arrays for reconstruction pipeline requirements
full_comp_deltas = []

# -------- MATPLOTLIB DAEMON MAPPING --------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('IoT Edge Compression Pipeline Monitor', fontsize=14)

def animate(i):
    """Matplotlib updating thread fetching mapped memory structures."""
    global timeout_triggered
    
    if timeout_triggered:
        # Trigger thread-safe visual closure terminating main loop execution
        plt.close('all')
        return

    with data_lock:
        if not raw_times:
            return
            
        x_raw = list(raw_times)
        y_raw = list(raw_values)
        x_comp = list(comp_times)
        y_comp = list(comp_values)
        
    ax1.clear()
    ax2.clear()

    # Subplot 1: Raw telemetry readings
    ax1.plot(x_raw, y_raw, color='blue', label='Raw Sensor Input')
    ax1.set_title('Sensor Readings')
    ax1.set_xlabel('System Ticks')
    ax1.set_ylabel('Temperature (C°)')
    ax1.grid(True)
    ax1.legend(loc='upper right')

    # Subplot 2: Retained payload map correlating DRR limits
    ax2.plot(x_raw, y_raw, color='lightgray', linestyle='--')
    ax2.scatter(x_comp, y_comp, color='red', s=60, label='Transmitted TX Nodes', zorder=5)
    
    if len(x_comp) > 1:
        ax2.plot(x_comp, y_comp, color='red', linewidth=1.5, zorder=4)

    if len(x_raw) > 0 and len(x_comp) > 0:
        drr = (1.0 - (len(x_comp) / len(x_raw))) * 100
        ax2.set_title(f'Cloud Payload Mapping [DRR: {drr:.0f}%]')
    else:
        ax2.set_title('Cloud Payload Mapping')
        
    ax2.set_xlabel('System Ticks')
    ax2.set_ylabel('Temperature (C°)')
    ax2.grid(True)
    ax2.legend(loc='upper right')

def generate_final_metrics():
    """Called after stream shuts down to print analysis and draw final graphs."""
    if len(full_raw_times) == 0:
        print("No stream data received. Exiting.")
        return
        
    print("--------------------------------------------------")
    print("        STREAM COMPRESSION FINAL REPORT           ")
    print("--------------------------------------------------")
    
    times_arr = np.array(full_raw_times)
    original_data = np.array(full_raw_values)
    comp_tx_deltas = np.array(full_comp_deltas)
    comp_t_arr = np.array(full_comp_times)
    
    # Mathematical reconstruction structure mapping
    reconstructed_sig = reconstruct_signal(
        total_length=len(times_arr),
        comp_times=comp_t_arr,
        comp_tx_deltas=comp_tx_deltas,
        method='linear' 
    )
    
    # Requirement: DRR and RMSE algorithm invocations
    drr = calculate_drr(len(original_data), len(comp_t_arr))
    rmse = calculate_rmse(original_data, reconstructed_sig)
    
    print(f"Total Stream Length      : {len(original_data)} points")
    print(f"Packets actually sent    : {len(comp_t_arr)} packets")
    print(f"Bandwidth Data Reduction : {drr:.2f}%")
    print(f"Reconstruction Loss RMSE : {rmse:.4f}")
    print("--------------------------------------------------")
    
    print("Opening Final Post-Stream Evaluation Static Graphs.")
    plot_reconstruction(times_arr, original_data, reconstructed_sig, f"Final Original vs Reconstructed Signal (DRR={drr:.0f}%, RMSE={rmse:.2f})", block=False)
    
    absolute_transmitted_values = reconstructed_sig[comp_t_arr]
    plot_transmitted_points(times_arr, original_data, comp_t_arr, absolute_transmitted_values, 
                            f"Final Active Stream Bandwidth Map", block=True)

if __name__ == '__main__':
    try:
        print("Daemon Server Component initializing...")
        # Instantiate background mapping threads per architecture restrictions
        server_thread = threading.Thread(target=run_flask)
        server_thread.daemon = True
        server_thread.start()
        
        monitor_thread = threading.Thread(target=monitor_timeout)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("Metrics component launching...\n")
        print("Waiting for Data Fetch Configurations...")
        
        ani = animation.FuncAnimation(fig, animate, interval=500, cache_frame_data=False)
        plt.tight_layout()
        # Execute main thread blocking structure for visual generation
        plt.show() 
        
        # Process return sequences post-shutdown
        if timeout_triggered:
            generate_final_metrics()
            
    except KeyboardInterrupt:
        pass  # Graciously handle exit without printing stack trace
        
    finally:
        print("\nProcess termination commanded.")
        sys.exit(0)
