import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

def calculate_adaptive_thresholds(
    values: np.ndarray, 
    window_size: int = 10, 
    k: float = 2.0,
    min_epsilon: float = 0.05
) -> np.ndarray:
    """
    Computes an adaptive threshold (epsilon) for each point based on the standard 
    deviation of a sliding window of recent values.
    
    Formula: epsilon = k * sigma_recent
    
    This is useful in tandem with SDT or Delta encoding when signal volatility 
    changes over time, requiring the compression algorithm to automatically loosen 
    or tighten its error bounds.
    
    Args:
        values: 1D NumPy array of sensor values.
        window_size: Number of recent points to include in the sliding window.
        k: Multiplier parameter (higher k means more aggressive compression).
        min_epsilon: A minimum fallback threshold to avoid epsilon dropping to zero.
        
    Returns:
        1D NumPy array of adaptive thresholds (same length as values).
    """
    n = len(values)
    if n == 0:
        return np.array([])
        
    if window_size < 2:
        return np.full(n, min_epsilon)
        
    # Pad the values at the beginning to preserve array length during windowing.
    # mode='edge' repeats the first array element to simulate early stability.
    padded_values = np.pad(values, (window_size - 1, 0), mode='edge')
    
    # Extract overlapping windows across the array incredibly fast
    windows = sliding_window_view(padded_values, window_shape=window_size)
    
    # Calculate sample standard deviation across each window (axis=1)
    sigma_recent = np.std(windows, axis=1, ddof=1)
    
    # Calculate epsilon
    thresholds = k * sigma_recent
    
    # Apply minimum epsilon threshold to prevent dividing by zero errors or breaking algorithms
    thresholds = np.clip(thresholds, min_epsilon, None)
    
    return thresholds
