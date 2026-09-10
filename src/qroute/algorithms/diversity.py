import numpy as np
from typing import List

def swarm_diversity(particles_positions: List[np.ndarray]) -> float:
    """
    Computes the diversity of a swarm based on the mean Euclidean distance
    of each particle to the swarm's center of mass (mean position).
    
    D = (1/N) * sum(distance(S_i, S_mean))
    """
    if not particles_positions:
        return 0.0
        
    swarm_matrix = np.array(particles_positions)
    s_mean = np.mean(swarm_matrix, axis=0)
    
    distances = np.linalg.norm(swarm_matrix - s_mean, axis=1)
    return float(np.mean(distances))
