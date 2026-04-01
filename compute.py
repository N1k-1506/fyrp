import numpy as np
from data.generator import generate_temperature_data
from metrics.evaluation import calculate_drr, calculate_rmse
from main import run_pipeline

def compute_metrics():
    print("Generating standard 1000-sample sensor waveform (Base 22C, varying sine noise)...\n")
    original_data = generate_temperature_data(num_samples=1000, base_temp=22.0, amplitude=6.0, noise_std=0.4, cycles=3.0)

    print("=============================================")
    print("   COMPRESSION METRICS BY THRESHOLD (k)     ")
    print("=============================================\n")

    for k_val in [1.5, 2.0, 2.5, 3.0, 4.0]:
        # Run streaming evaluation framework natively
        comp, reconstructed = run_pipeline(original_data, k=k_val)
        comp_times, _ = comp
        
        # Calculate isolated metrics
        transmissions = len(comp_times)
        drr = calculate_drr(1000, transmissions)
        rmse = calculate_rmse(original_data, reconstructed)
        
        print(f"--- Threshold Multiplier: k={k_val} ---")
        print(f" Original Data Length : 1000 samples")
        print(f" Total Transmissions  : {transmissions} payload network dispatches")
        print(f" Data Reduction Ratio : {drr:.2f}x Hardware Savings")
        print(f" Computed RMSE        : {rmse:.4f} °C Structural Deviation\n")

if __name__ == "__main__":
    compute_metrics()
