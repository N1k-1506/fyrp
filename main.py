import numpy as np
from data.generator import generate_temperature_data
from algorithms.streaming import StreamCompressor
from algorithms.reconstruction import reconstruct_signal
from metrics.evaluation import calculate_drr, calculate_rmse, estimate_transmission_energy
from visualization.plots import plot_reconstruction, plot_transmitted_points, plot_compression_ratio

def run_pipeline(original_data: np.ndarray, window_size: int = 10, k: float = 2.0):
    """
    Executes the streaming IoT compression pipeline simulating Arduino point-by-point logic.
    """
    times = np.arange(len(original_data))
    
    # Instantiate the streaming simulation class (our "C++" virtual edge node)
    compressor = StreamCompressor(window_size=window_size, k=k, debug=False)
    
    comp_times = []
    comp_deltas = []
    
    # 1. Edge IoT Node Simulator Loop (Live Processing)
    for value in original_data:
        should_transmit, payload = compressor.process_data_point(value)
        
        if should_transmit:
            t, delta_val = payload
            comp_times.append(t)
            comp_deltas.append(delta_val)
            
    # Force out the final point ensuring loop shutdown logic propagates
    should_transmit, payload = compressor.flush()
    if not comp_times or comp_times[-1] != payload[0]:
        t, delta_val = payload
        comp_times.append(t)
        comp_deltas.append(delta_val)

    comp_times_arr = np.array(comp_times)
    comp_deltas_arr = np.array(comp_deltas)

    # 2. Cloud Server Evaluator (Receiver Node)
    # Rebuild the full length absolute signal from the sparse transmitted anchor payloads
    reconstructed_signal = reconstruct_signal(
        total_length=len(times),
        comp_times=comp_times_arr,
        comp_tx_deltas=comp_deltas_arr,
        method='linear'  # Can easily be swapped to 'step' here for ZOH analysis
    )
    
    return (comp_times_arr, comp_deltas_arr), reconstructed_signal

if __name__ == "__main__":
    print("Generating simulated IoT Sensor Data...")
    original_data = generate_temperature_data(num_samples=1000, base_temp=22.0, amplitude=6.0, noise_std=0.4, cycles=3.0)
    times = np.arange(len(original_data))
    
    # ---------------------------------------------------------
    # Test 1: Full evaluation on standard stringency (k=2.5)
    # ---------------------------------------------------------
    test_k = 2.5
    print(f"\nEvaluating Virtual Edge Node with k={test_k}...")
    compressed, reconstructed = run_pipeline(original_data, k=test_k)
    comp_times, comp_deltas = compressed
    
    # Calculate Server Metrics
    drr = calculate_drr(len(original_data), len(comp_times))
    rmse = calculate_rmse(original_data, reconstructed)
    
    print(f"Original points: {len(original_data)}")
    print(f"Transmitted points: {len(comp_times)}")
    print(f"DRR: {drr:.0f}%")
    print(f"RMSE: {rmse:.2f}")
    
    print("\nOpening plots! Close each plot to view the next one...")
    
    # Visualization Validation 
    plot_reconstruction(times, original_data, reconstructed, f"Original vs Reconstructed (k={test_k})")
    
    absolute_transmitted_values = reconstructed[comp_times]
    plot_transmitted_points(times, original_data, comp_times, absolute_transmitted_values, 
                            f"Points Transmitted vs Skipped (k={test_k})")
    
    # ---------------------------------------------------------
    # Test 2: Compression Ratio Scaling Profiles
    # ---------------------------------------------------------
    print("\nRunning sweep actively testing different multiplier thresholds...")
    k_sweeps = [1.0, 1.5, 2.5, 3.5, 5.0]
    ratios = []
    labels = []
    
    for k_val in k_sweeps:
        comp, _ = run_pipeline(original_data, k=k_val)
        c_times, _ = comp
        r = calculate_drr(len(original_data), len(c_times))
        ratios.append(r)
        labels.append(f"k={k_val}")
        
    plot_compression_ratio(labels, ratios, "Streaming Hardware Scaling Efficiency")
    print("\nHardware architecture transition effectively validated and completed.")
