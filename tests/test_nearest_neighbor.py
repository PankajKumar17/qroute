import pytest
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.nearest_neighbor import nearest_neighbor_vrp

def test_nearest_neighbor_vrp():
    n_nodes = 20
    G = build_synthetic_graph(n_nodes, seed=42)
    n_customers = n_nodes - 1
    
    demands = list(np.random.randint(5, 20, size=n_customers))
    vehicle_capacity = 50
    
    routes = nearest_neighbor_vrp(G, demands, vehicle_capacity)
    
    assert len(routes) > 0
    
    flattened = [c for r in routes for c in r]
    # Check if every customer is visited
    assert set(flattened) == set(range(n_customers))
    assert len(flattened) == n_customers
    
    # Check capacity constraints
    for r in routes:
        assert sum(demands[c] for c in r) <= vehicle_capacity
