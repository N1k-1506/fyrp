import numpy as np
from typing import Union

def compress(times: np.ndarray, values: np.ndarray, deviation: Union[float, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """
    Applies the Swinging Door Trending (SDT) algorithm to compress time-series data.
    This is a lossy compression algorithm that drops data points that fall within
    a defined error bound (deviation) from a tracked linear trend.
    
    Args:
        times: 1D NumPy array of timestamps or continuous indices.
        values: 1D NumPy array of corresponding sensor values.
        deviation: The maximum allowed absolute error (epsilon) for compression. 
                   Can be a single float or a NumPy array of thresholds for adaptive compression.
        
    Returns:
        A tuple of two NumPy arrays: (compressed_times, compressed_values)
    """
    if len(times) != len(values):
        raise ValueError("Times and values must have the same length.")
        
    is_array_dev = isinstance(deviation, np.ndarray)
    if is_array_dev and len(deviation) != len(values):
        raise ValueError("Deviation array must have the same length as values.")
        
    # Standard check: Cannot compress arrays with 2 points or fewer
    if len(times) <= 2:
        return times.copy(), values.copy()
        
    # We must always keep the very first data point
    comp_times = [times[0]]
    comp_values = [values[0]]
    
    # Store our current starting position for the "doors" (the pivot point)
    t0, v0 = times[0], values[0]
    
    # max_slope drops over time (the "Upper Door" swings down)
    # min_slope rises over time (the "Lower Door" swings up)
    max_slope = float('inf')
    min_slope = float('-inf')
    
    last_saved_idx = 0
    
    for i in range(1, len(times)):
        t_i = times[i]
        v_i = values[i]
        dev_i = deviation[i] if is_array_dev else deviation
        
        # Avoid division by zero problems
        dt = t_i - t0
        if dt == 0:
            continue
            
        # Calculate maximum and minimum allowable slopes to the new point
        # including our deviation window bounds
        current_max_slope = (v_i + dev_i - v0) / dt
        current_min_slope = (v_i - dev_i - v0) / dt
        
        # The doors continually constrain inward.
        max_slope = min(max_slope, current_max_slope)
        min_slope = max(min_slope, current_min_slope)
        
        # When max_slope < min_slope, our doors have crossed!
        # The line trend isn't valid against the new point anymore.
        if max_slope < min_slope:
            # Save the immediately PRECEDING point, as that's where the trend safely died
            prev_idx = i - 1
            comp_times.append(times[prev_idx])
            comp_values.append(values[prev_idx])
            last_saved_idx = prev_idx
            
            # Form a new pivot starting identically from that preceding point
            t0 = times[prev_idx]
            v0 = values[prev_idx]
            
            # Recalculate our doors considering only the new pivot and current point
            dt_new = t_i - t0
            if dt_new > 0:
                max_slope = (v_i + dev_i - v0) / dt_new
                min_slope = (v_i - dev_i - v0) / dt_new
            else:
                max_slope = float('inf')
                min_slope = float('-inf')
                
    # We must always retain the very last data point as well
    if last_saved_idx != len(times) - 1:
        comp_times.append(times[-1])
        comp_values.append(values[-1])
        
    return np.array(comp_times), np.array(comp_values)
