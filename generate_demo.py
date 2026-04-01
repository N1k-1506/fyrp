import numpy as np
import matplotlib.pyplot as plt
from data.generator import generate_temperature_data
from main import run_pipeline
from visualization.plots import plot_reconstruction, plot_transmitted_points

def export_artifacts():
    print("Evaluating signal sweeps...")
    original = generate_temperature_data(1000, 22.0, 6.0, 0.4, 3.0)
    times = np.arange(1000)

    comp, recon = run_pipeline(original, k=2.5)
    comp_times, _ = comp

    print("Generating Signal Plots...")
    plot_reconstruction(times, original, recon, "Original vs Reconstructed (k=2.5)")
    plt.savefig(r'C:\Users\nkrai\.gemini\antigravity\brain\a2d201f0-9448-488f-a419-1a2136f1c844\artifacts\reconstruction.png', bbox_inches='tight')
    plt.close('all')

    abs_trans = recon[comp_times]
    plot_transmitted_points(times, original, comp_times, abs_trans, "Points Transmitted vs Skipped (k=2.5)")
    plt.savefig(r'C:\Users\nkrai\.gemini\antigravity\brain\a2d201f0-9448-488f-a419-1a2136f1c844\artifacts\transmitted.png', bbox_inches='tight')
    plt.close('all')
    print("Demo graphics exported successfully.")

if __name__ == '__main__':
    export_artifacts()
