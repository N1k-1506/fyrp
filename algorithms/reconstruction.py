import numpy as np
from algorithms.delta import decode

def reconstruct_signal(
    total_length: int, 
    comp_times: np.ndarray, 
    comp_tx_deltas: np.ndarray, 
    method: str = 'linear'
) -> np.ndarray:
    """
    Rebuilds the original full-length physical signal exclusively natively from the sparse transmitted payload deltas.
    
    Args:
        total_length: Expectation vector mapped sample timeframe limitation.
        comp_times: Array of timestamps specifically tracking successful packets.
        comp_tx_deltas: Array sequentially handling mathematically encoded Delta payloads directly from Anchor endpoints.
        method: Interpolation strategy ('linear' models native SDT; 'step' enforces zero-order constraints.)
                
    Returns:
        1D NumPy array reconstructing completely precise absolute structure curves locally.
    """
    if len(comp_times) == 0:
        return np.zeros(total_length)
        
    full_times = np.arange(total_length)
    
    # 1. Delta Decoding (Decode the physical payload bytes robustly sequentially back into absolute temperature bounds)
    absolute_anchors = decode(comp_tx_deltas)
    
    if method == 'linear':
        # 2. Linear Interoplation Layer (Native SDT Standard Default mapping connecting directly tracking points)
        reconstructed_signal = np.interp(full_times, comp_times, absolute_anchors)
        return reconstructed_signal
        
    elif method == 'step':
        # Step Interpolation Layer (Zero-Order Hold mapping explicitly tracking backward gaps flatlining values natively)
        reconstructed_signal = np.zeros(total_length)
        current_idx = 0
        
        for i in range(len(comp_times)):
            t = int(comp_times[i])
            val = absolute_anchors[i]
            
            if i == 0:
                reconstructed_signal[t] = val
                current_idx = t + 1
            else:
                last_val = absolute_anchors[i-1]
                reconstructed_signal[current_idx:t] = last_val
                reconstructed_signal[t] = val
                current_idx = t + 1
                
        # Top off cleanly over the unmapped ceiling limits 
        if current_idx < total_length:
            reconstructed_signal[current_idx:] = absolute_anchors[-1]
            
        return reconstructed_signal
    
    else:
        raise ValueError(f"Unknown reconstruction method: {method}")
