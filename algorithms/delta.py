import numpy as np

def encode(data: np.ndarray) -> np.ndarray:
    """
    Applies delta encoding to 1D time-series data.
    
    Args:
        data: 1D NumPy array of the original data.
        
    Returns:
        1D NumPy array representing the delta encoded data.
    """
    if len(data) == 0:
        return np.array([])
    
    deltas = np.diff(data)
    encoded_data = np.concatenate(([data[0]], deltas))
    return encoded_data

def decode(encoded_data: np.ndarray) -> np.ndarray:
    """
    Decodes delta encoded time-series data.
    
    Args:
        encoded_data: 1D NumPy array of delta encoded data.
        
    Returns:
        1D NumPy array representing the reconstructed original data.
    """
    if len(encoded_data) == 0:
        return np.array([])
        
    decoded_data = np.cumsum(encoded_data)
    return decoded_data
