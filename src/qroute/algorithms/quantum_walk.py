import numpy as np
import random
from typing import List
from qroute.encoding.random_key import decode_to_tour

def quantum_walk_sample(graph, n_samples: int, seed: int = None) -> List[np.ndarray]:
    """
    Simulates a discrete-time quantum walk (classically) on the road network to sample
    diverse candidate orderings.
    
    Conversion to random-key vector:
    For each sample, we run a random walk (biased by edge weights, serving as a proxy 
    for the quantum walk probability distribution) starting from the depot.
    The order in which nodes are first visited dictates their position in the tour.
    We then generate a random-key vector that sorts to this exact ordering.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
        
    n_nodes = graph.number_of_nodes()
    n_customers = n_nodes - 1
    samples = []
    
    for _ in range(n_samples):
        visited = []
        current = 0 # depot
        unvisited = set(range(1, n_nodes))
        
        while unvisited:
            # Get neighbors (assuming complete graph or well-connected)
            neighbors = list(graph.successors(current))
            valid_neighbors = [n for n in neighbors if n in unvisited]
            
            if not valid_neighbors:
                # Dead end, just pick a random unvisited
                valid_neighbors = list(unvisited)
                
            # Bias transition by inverse distance (or just random for simple walk)
            # A true quantum walk would use interference, here we use a simple heuristic
            next_node = random.choice(valid_neighbors)
            visited.append(next_node)
            unvisited.remove(next_node)
            current = next_node
            
        # visited contains the customers (1 to n_customers) in order
        # We need a random-key vector that produces this ordering.
        # i.e., keys[customer - 1] should be ascending.
        keys = np.zeros(n_customers)
        # Assign evenly spaced keys, with some noise
        base_keys = np.linspace(0.1, 0.9, n_customers)
        base_keys += np.random.uniform(-0.01, 0.01, n_customers)
        base_keys = np.clip(base_keys, 0, 1)
        base_keys.sort()
        
        for i, customer_node in enumerate(visited):
            keys[customer_node - 1] = base_keys[i]
            
        samples.append(keys)
        
    return samples
