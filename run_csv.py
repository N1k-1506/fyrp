import csv
import numpy as np
import matplotlib
matplotlib.use('Agg') # Run headless to just generate the image files
import matplotlib.pyplot as plt
from main import run_pipeline
from metrics.evaluation import calculate_drr, calculate_rmse, estimate_transmission_energy
from visualization.plots import plot_reconstruction, plot_transmitted_points

def run():
    print("Loading dataset from training_dataset.csv...")
    original_data = []
    
    with open("training_dataset.csv", "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            original_data.append(float(row[2]))

    original_data = np.array(original_data)
    test_k = 0.5 
    print(f"Running Streaming Compression Pipeline (k={test_k})...")

    compressed, reconstructed = run_pipeline(original_data, k=test_k)
    comp_times, _ = compressed

    drr = calculate_drr(len(original_data), len(comp_times))
    rmse = calculate_rmse(original_data, reconstructed)
    energy = estimate_transmission_energy(len(comp_times))

    print("\n---------------------------------------------------------")
    print(f"Bandwidth Reduction (DRR)   : {drr:.2f}%")
    print(f"Reconstruction Error (RMSE) : {rmse:.4f}")
    print(f"Estimated Energy Use        : {energy:.4f} J")
    
    times = np.arange(len(original_data))
    absolute_transmitted_values = reconstructed[comp_times]
    
    print("\nSaving high-resolution graphs for your PowerPoint...")
    
    # 1. Reconstruction Plot
    plot_reconstruction(times, original_data, reconstructed, title="Original vs Reconstructed Signal (15-point Sample)", block=False)
    plt.savefig("ppt_reconstruction_graph.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Points Transmitted Plot
    plot_transmitted_points(times, original_data, comp_times, absolute_transmitted_values, title="Transmitted Points vs Skipped (15-point Sample)", block=False)
    plt.savefig("ppt_transmitted_graph.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("- 'ppt_reconstruction_graph.png' created.")
    print("- 'ppt_transmitted_graph.png' created.")

if __name__ == "__main__":
    run()
