import numpy as np

def encode_particle(n_customers: int, seed: int = None) -> np.ndarray:
    """
    Generates a random continuous key vector for a particle.
    
    Args:
        n_customers: Number of customers (length of vector).
        seed: Random seed.
        
    Returns:
        1D numpy array of random floats between 0 and 1.
    """
    if seed is not None:
        np.random.seed(seed)
    return np.random.uniform(0, 1, size=n_customers)

def decode_to_tour(keys: np.ndarray) -> list[int]:
    """
    Decodes a random-key vector into a giant tour by sorting indices based on key values.
    
    Args:
        keys: 1D numpy array of floats.
        
    Returns:
        A permutation (list of indices from 0 to len(keys)-1).
        Note: The depot (usually 0) is typically not part of these keys, 
        so these indices usually represent customers (e.g., customer i = index + 1).
    """
    return list(np.argsort(keys))
