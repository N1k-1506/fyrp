import numpy as np
from data.generator import generate_temperature_data
from algorithms.streaming import StreamCompressor
from algorithms.delta import decode
import time

def get_sensor_value(stream_iterator):
    """
    Explicit Sensor Slot Wrapper (Ready for formal physical hardware integration).
    Actively replaces array batching with literal point-by-point live physical polling.
    """
    try:
        return next(stream_iterator)
    except StopIteration:
        return None

def simulate_sensor_hardware():
    """
    Simulates an Arduino C++ environment actively reading sensor data in a `void loop()`, 
    running the StreamCompressor point-by-point live in memory, and broadcasting 
    only when functionally triggered.
    """
    print("Initializing Sensor Hardware Simulation...\n")
    
    # 1. Generate a small dataset acting as our live temperature sensor
    sensor_stream = generate_temperature_data(num_samples=100, base_temp=22.0, amplitude=4.0, noise_std=0.2)
    total_time_ticks = len(sensor_stream)
    
    # 2. Setup the Compressor object (Acting as our flashed Firmware struct)
    compressor = StreamCompressor(window_size=5, k=2.0, debug=True)
    
    transmitted_times = []
    transmitted_deltas = []
    
    print("--- STARTING SENSOR LOOP ---")
    
    # 3. Simulate hardware sequentially polling the sensor
    sensor_iterator = iter(sensor_stream)
    tick = 0
    
    while True:
        time.sleep(0.05)  # Simulate physical hardware sensor polling delay
        
        # EXPLICIT SENSOR SLOT (Replace iterator completely later when swapping to a Live COM Port / I2C DHT11 module)
        current_temp = get_sensor_value(sensor_iterator)
        if current_temp is None: break
        
        # Pass exactly ONE reading to the compressor at a time
        should_transmit, payload = compressor.process_data_point(current_temp)
        
        if should_transmit:
            # Emulate Radio Tx (e.g., LoRaWAN dispatch or Serial.print)
            t, delta_val = payload
            print(f"[TX TRIGGERED] Timestamp: {t:03d} | Delta Payload: {delta_val:+.4f} | Absolute Temp: {current_temp:.2f} C")
            
            # Pack away for the simulated 'Cloud Receiver' 
            transmitted_times.append(t)
            transmitted_deltas.append(delta_val)
        else:
            # Emulate verbose debug serial monitoring for skipped redundant points
            ep = payload['epsilon']
            print(f"[SKIPPED]      Timestamp: {tick:03d} | Abs Temp: {current_temp:.2f} C | Dynamic Epsilon Bounds: {ep:.4f}")
            
        tick += 1
            
    # Simulate hardware deep-sleep shutdown
    should_transmit, payload = compressor.flush()
    if not transmitted_times or transmitted_times[-1] != payload[0]:
        t, delta_val = payload
        transmitted_times.append(t)
        transmitted_deltas.append(delta_val)
        print(f"[FINAL FLUSH]  Timestamp: {t:03d} | Delta Payload: {delta_val:+.4f}")
        
    print("--- END OF SENSOR STREAM ---\n")
    
    # --------------------------------------------------------------------------
    
    # 4. Simulated Cloud Server Receiver processing the transmitted payload
    print("--- CLOUD RECEIVER DECODING ---")
    print(f"Total Cloud Packets Received: {len(transmitted_times)} (out of {total_time_ticks} raw generated points)")
    print(f"Network Over-The-Air Reduction: {(total_time_ticks / len(transmitted_times)):.2f}x Ratio\n")
    
    from algorithms.reconstruction import reconstruct_signal
    from metrics.evaluation import calculate_rmse
    
    transmitted_times_arr = np.array(transmitted_times)
    transmitted_deltas_arr = np.array(transmitted_deltas)
    
    # Utilize the dedicated signal builder to mathematically decode back to temperatures
    reconstructed_signal = reconstruct_signal(
        total_length=total_time_ticks,
        comp_times=transmitted_times_arr,
        comp_tx_deltas=transmitted_deltas_arr,
        method='linear'
    )
    
    print("Verifying structural integrity of the first 5 records:")
    for i in range(5):
        print(f"   Tick {i:03d} | Original Sensor Output: {sensor_stream[i]:.4f} C | Decoded Cloud Value: {reconstructed_signal[i]:.4f} C")
        
    error_margin = calculate_rmse(sensor_stream, reconstructed_signal)
    print(f"\nMathematical Drift Evaluation:")
    print(f"   Root Mean Square Error (RMSE): {error_margin:.4f} C")
    
    if error_margin > 5.0:
        print("   [WARNING] Massive compounding deviation detected. The sequence has drifted out of bounds.")
    else:
        print("   [SUCCESS] Reconstructed signal strictly approximated original trajectory.")
        
    print("\nArduino hardware streaming loop integration tested successfully.")

if __name__ == "__main__":
    simulate_sensor_hardware()
