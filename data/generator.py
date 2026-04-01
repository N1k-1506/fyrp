import numpy as np

def generate_temperature_data(num_samples: int = 1000, 
                              base_temp: float = 20.0, 
                              amplitude: float = 10.0, 
                              noise_std: float = 1.5,
                              cycles: float = 5.0) -> np.ndarray:
    """
    Generates realistic IoT temperature sensor data.
    Uses a sine wave to simulate daily temperature trends and adds Gaussian noise.
    
    Args:
        num_samples: Number of data points to generate.
        base_temp: The average base temperature.
        amplitude: The amplitude of the sine wave (temperature variation).
        noise_std: Standard deviation of the Gaussian noise.
        cycles: Number of complete sine wave cycles (e.g., days) over the samples.
        
    Returns:
        NumPy array of simulated temperature readings.
    """
    # Create a time array
    x = np.linspace(0, cycles * 2 * np.pi, num_samples)
    
    # Base trend using sine wave
    trend = base_temp + amplitude * np.sin(x)
    
    # Add Gaussian noise
    noise = np.random.normal(0, noise_std, num_samples)
    
    # Combine trend and noise
    temperature_data = trend + noise
    
    return temperature_data
