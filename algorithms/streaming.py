import math
from typing import Optional, Tuple, Any, List

class StreamCompressor:
    """
    A stateful point-by-point compressor configured specifically for easy portability 
    to Arduino/C++ IoT microcontrollers.
    
    This version correctly solves Mathematical Drift by computing SDT directly against
    absolute hardware values natively, and subsequently Delta-Encoding the verified 
    anchor points prior to emitting the network payload!
    """
    def __init__(self, window_size: int = 10, k: float = 2.0, min_epsilon: float = 0.05, debug: bool = False):
        self.window_size = window_size
        self.k = k
        self.min_epsilon = min_epsilon
        self.debug = debug
        
        # Hardware Tick Counter 
        self.t = 0
        
        # 1. Delta Memory State (Used strictly for volatility analysis)
        self.last_value: Optional[float] = None
        
        # 2. Threshold Memory State (Circular Buffer simulating a fixed C++ array)
        self.delta_queue: List[float] = []
        self.queue_index = 0
        
        # 3. SDT Memory State (Now operates identically upon absolute bounds)
        self.t_pivot = 0
        self.v_pivot = 0.0
        self.max_slope = float('inf')
        self.min_slope = float('-inf')
        self.last_t = 0
        self.last_abs_value = 0.0
        
        # 4. Network Radio Transmitter State (For Payload Delta Encoding)
        # We track specifically the last absolute value we successfully emitted 
        # so we can compute the structural bytes to save space.
        self.last_transmitted_abs_value = 0.0
        
        self.sdt_initialized = False

    def process_data_point(self, value: float) -> Tuple[bool, Any]:
        """
        Takes a new absolute sensor reading and advances the compression pipeline.
        Returns: (should_transmit, (t, delta_payload))
        """
        # --- 1. Bootstrapping Layer ---
        if self.last_value is None: 
            self.last_value = value
            self.t_pivot = self.t
            self.v_pivot = value 
            self.last_t = self.t
            self.last_abs_value = value
            self.last_transmitted_abs_value = value
            self.sdt_initialized = True
            
            self._update_threshold_queue(0.0)
            
            # Unconditionally transmit the very first base point block for stable reconstruction
            output = (self.t, value)
            self.t += 1
            return True, output
            
        current_delta = value - self.last_value
        self.last_value = value
        
        # --- 2. Adaptive Thresholding Layer ---
        # Notice we still feed the *relative delta* sequence into the buffer cleanly
        # to correctly analyze standard deviation (volatility) of the signal!
        self._update_threshold_queue(current_delta)
        epsilon = self._calculate_epsilon()
        
        # --- 3. SDT Compression Layer ---
        # SDT computes safely natively mapping onto the TRUE Absolute value
        should_transmit, payload = self._sdt_step(self.t, value, epsilon)
        
        self.t += 1
        return should_transmit, payload
        
    def _update_threshold_queue(self, delta: float) -> None:
        if len(self.delta_queue) < self.window_size:
            self.delta_queue.append(delta)
        else:
            self.delta_queue[self.queue_index] = delta
            self.queue_index = (self.queue_index + 1) % self.window_size
            
    def _calculate_epsilon(self) -> float:
        n = len(self.delta_queue)
        if n < 2:
            return self.min_epsilon
            
        mean = sum(self.delta_queue) / n
        variance = sum((x - mean) ** 2 for x in self.delta_queue) / (n - 1)
        std_dev = math.sqrt(variance)
        
        epsilon = self.k * std_dev
        return max(epsilon, self.min_epsilon)
        
    def _sdt_step(self, t: int, current_abs_value: float, epsilon: float) -> Tuple[bool, Any]:
        dt = t - self.t_pivot
        
        if dt == 0:
            return False, None
            
        current_max_slope = (current_abs_value + epsilon - self.v_pivot) / dt
        current_min_slope = (current_abs_value - epsilon - self.v_pivot) / dt
        
        new_max_slope = min(self.max_slope, current_max_slope)
        new_min_slope = max(self.min_slope, current_min_slope)
        
        should_transmit = False
        processed_value = None
        
        # Have the sliding doors crossed each other?
        if new_max_slope < new_min_slope:
            should_transmit = True
            
            # --- STRUCTURE TARGET PAYLOAD TRANSMISSION ---
            # To aggressively save network packet sizes across the wire, 
            # we Delta-Encode the Absolute Anchors locally immediately prior to dispatch!
            tx_delta = self.last_abs_value - self.last_transmitted_abs_value
            processed_value = (self.last_t, tx_delta)
            
            self.last_transmitted_abs_value = self.last_abs_value
            
            # Spin up a brand new linear trend window dynamically locked to exactly that last point
            self.t_pivot = self.last_t
            self.v_pivot = self.last_abs_value
            
            dt_new = t - self.t_pivot
            if dt_new > 0:
                self.max_slope = (current_abs_value + epsilon - self.v_pivot) / dt_new
                self.min_slope = (current_abs_value - epsilon - self.v_pivot) / dt_new
            else:
                self.max_slope = float('inf')
                self.min_slope = float('-inf')
        else:
            self.max_slope = new_max_slope
            self.min_slope = new_min_slope
            
        # Push variables forward to volatile memory  
        self.last_t = t
        self.last_abs_value = current_abs_value
        
        if not should_transmit and self.debug:
            processed_value = {'time': t, 'abs': current_abs_value, 'epsilon': epsilon, 'status': 'skipped'}
                 
        return should_transmit, processed_value
        
    def flush(self) -> Tuple[bool, Any]:
        tx_delta = self.last_abs_value - self.last_transmitted_abs_value
        self.last_transmitted_abs_value = self.last_abs_value
        return True, (self.last_t, tx_delta)
