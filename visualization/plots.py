import matplotlib.pyplot as plt
import numpy as np

def plot_reconstruction(original_times: np.ndarray, original_data: np.ndarray, 
                        reconstructed_data: np.ndarray, title: str = "Original vs Reconstructed Signal"):
    """
    Plots the original signal against the lossy-reconstructed signal.
    This effectively visualizes the error introduced by compression.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(original_times, original_data, label='Original Signal', color='#1f77b4', alpha=0.7, linewidth=2)
    plt.plot(original_times, reconstructed_data, label='Reconstructed Signal', color='#d62728', linestyle='--', linewidth=1.5)
    
    plt.xlabel('Time (samples)')
    plt.ylabel('Sensor Value')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_transmitted_points(original_times: np.ndarray, original_data: np.ndarray, 
                            comp_times: np.ndarray, comp_values: np.ndarray, 
                            title: str = "Points Transmitted vs Skipped"):
    """
    Plots the full original signal but specifically marks which points were actually 
    transmitted (kept by compression) versus which were skipped (dropped).
    """
    plt.figure(figsize=(12, 6))
    
    # Plot the full background signal (representing all generated/skipped data)
    plt.plot(original_times, original_data, label='Original Data (Skipped)', 
             color='gray', alpha=0.4, linestyle='-', linewidth=1.5)
             
    # Scatter plot the specific anchor points that survived SDT compression
    plt.scatter(comp_times, comp_values, color='#2ca02c', label='Transmitted Points', zorder=5, s=30)
    
    # Draw the approximated trend lines bounding those transmitted points
    plt.plot(comp_times, comp_values, color='#2ca02c', alpha=0.8, linewidth=1.5, label='Transmitted Trend')
    
    plt.xlabel('Time (samples)')
    plt.ylabel('Sensor Value')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_compression_ratio(categories: list[str], ratios: list[float], title: str = "Compression Ratio Comparison"):
    """
    Creates a bar chart to graphically compare compression ratios (DRR) across 
    different algorithms or configurations (e.g., varying epsilon thresholds).
    """
    plt.figure(figsize=(9, 6))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Dynamically grab enough colors based on the number of bars
    bars = plt.bar(categories, ratios, color=colors[:len(categories)])
    
    # Add numerical labels cleanly on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + (max(ratios) * 0.02), 
                 f'{yval:.2f}x', ha='center', va='bottom', fontweight='bold')
                 
    plt.ylabel('Data Reduction Ratio (DRR)')
    plt.title(title)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Make the bottom edge look solid against the grid
    plt.axhline(0, color='black', linewidth=1)
    
    plt.tight_layout()
    plt.show()
