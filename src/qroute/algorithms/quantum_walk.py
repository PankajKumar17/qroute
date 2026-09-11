import numpy as np
from scipy.stats import qmc
from typing import List

def uniform_random_sample(n_customers: int, n_samples: int, seed: int = None) -> List[np.ndarray]:
    if seed is not None:
        np.random.seed(seed)
    return [np.random.uniform(0, 1, size=n_customers) for _ in range(n_samples)]

def lhs_sample(n_customers: int, n_samples: int, seed: int = None) -> List[np.ndarray]:
    sampler = qmc.LatinHypercube(d=n_customers, seed=seed)
    samples = sampler.random(n=n_samples)
    return [samples[i, :] for i in range(n_samples)]

def quantum_walk_sample(n_customers: int, n_samples: int, seed: int = None) -> List[np.ndarray]:
    """
    Simulates a discrete-time quantum walk classically on a cycle graph of customers.
    This is a classical simulation of quantum walk dynamics (Hadamard coin + conditional shift),
    used only for diversity-oriented sampling, with no computational-advantage or hardware claim.
    """
    if seed is not None:
        np.random.seed(seed)
        
    samples = []
    T = min(15, n_customers) # Walk steps
    
    Hadamard = np.array([[1, 1], [1, -1]]) / np.sqrt(2.0)
    
    for s in range(n_samples):
        # State vector for cycle graph: shape (n_customers, 2)
        # Coin states: 0 = Left, 1 = Right
        psi = np.zeros((n_customers, 2), dtype=complex)
        
        # Pick a random starting node to ensure diversity across samples
        start_node = np.random.randint(0, n_customers)
        # Random complex amplitudes for the initial coin state
        psi[start_node, 0] = np.cos(np.random.uniform(0, 2*np.pi)) + 1j * np.sin(np.random.uniform(0, 2*np.pi))
        psi[start_node, 1] = np.cos(np.random.uniform(0, 2*np.pi)) + 1j * np.sin(np.random.uniform(0, 2*np.pi))
        psi /= np.linalg.norm(psi)
        
        for t in range(T):
            # Apply unitary Hadamard coin operator
            psi = np.einsum('ij,xj->xi', Hadamard, psi)
            
            # Apply conditional shift operator
            psi_next = np.zeros_like(psi)
            for x in range(n_customers):
                # Coin 0: Move Left (x-1)
                psi_next[(x - 1) % n_customers, 0] = psi[x, 0]
                # Coin 1: Move Right (x+1)
                psi_next[(x + 1) % n_customers, 1] = psi[x, 1]
                
            psi = psi_next
            
        # Compute probability distribution (born rule)
        prob = np.abs(psi[:, 0])**2 + np.abs(psi[:, 1])**2
        
        # Use probability amplitude mapped to random key space
        prob_max = np.max(prob) if np.max(prob) > 0 else 1.0
        keys = (prob / prob_max) * 0.9 + np.random.uniform(0, 0.1, size=n_customers)
        keys = np.clip(keys, 0.0, 1.0)
        
        samples.append(keys)
        
    return samples
