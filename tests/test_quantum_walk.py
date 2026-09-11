import pytest
import numpy as np
import networkx as nx
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.quantum_walk import quantum_walk_sample
from qroute.encoding.random_key import decode_to_tour

def test_quantum_walk_sample():
    n_nodes = 10
    G = nx.cycle_graph(5, create_using=nx.DiGraph())
    n_samples = 5
    
    # Generate samples
    n_customers = len(G.nodes) - 1
    samples = quantum_walk_sample(n_customers, n_samples=n_samples, seed=42)
    
    assert len(samples) == n_samples
    
    # Check decode without error
    for keys in samples:
        tour = decode_to_tour(keys)
        assert len(tour) == len(G.nodes) - 1
        assert len(set(tour)) == len(G.nodes) - 1
        
    # Check diversity (pairwise distances > 0)
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            dist = np.linalg.norm(samples[i] - samples[j])
            assert dist > 0.01 # Not identical
