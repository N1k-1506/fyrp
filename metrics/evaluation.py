import numpy as np
def calculate_drr(original_size: int, compressed_size: int) -> float:
    """
    Calculates the Data Reduction Ratio (DRR) as a percentage of redundant data successfully dropped.
    """
    if original_size == 0:
        return 0.0
    return ((original_size - compressed_size) / float(original_size)) * 100.0
def calculate_rmse(original_data: np.ndarray, reconstructed_data: np.ndarray) -> float:
    """
    Calculates the Root Mean Square Error (RMSE) between the original
    signal and the lossy-reconstructed signal to evaluate compression fidelity.
    
    Args:
        original_data: 1D NumPy array of the original dataset.
        reconstructed_data: 1D NumPy array of the reconstructed dataset.
        
    Returns:
        float: The calculated Root Mean Square Error.
    """
    if len(original_data) != len(reconstructed_data):
        raise ValueError("Original and reconstructed data must have the exact same length.")
        
    mse = np.mean((original_data - reconstructed_data) ** 2)
    return float(np.sqrt(mse))

def estimate_transmission_energy(num_transmissions: int, energy_per_tx_joules: float = 0.015) -> float:
    """
    Estimates the total energy consumed for data transmission overhead.
    This effectively demonstrates battery savings on IoT edges when utilizing SDT.
    
    Args:
        num_transmissions: The number of data points actually transmitted.
        energy_per_tx_joules: The typical energy cost per transmission packet in Joules.
                              (e.g., 0.015J is an approximate baseline for low-power WiFi / LoRa)
        
    Returns:
        float: Total estimated energy burned over these transmissions in Joules.
    """
    return num_transmissions * energy_per_tx_joules
