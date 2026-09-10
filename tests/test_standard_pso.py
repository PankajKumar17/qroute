import pytest
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.standard_pso import standard_pso

def test_standard_pso_monotonicity():
    n_nodes = 10
    G = build_synthetic_graph(n_nodes, seed=42)
    n_customers = n_nodes - 1
    
    demands = [10] * n_customers
    vehicle_capacity = 30
    
    best_fitness, best_routes, history = standard_pso(
        G, demands, vehicle_capacity, swarm_size=10, iterations=10
    )
    
    assert best_fitness > 0
    assert np.isfinite(best_fitness)
    assert len(history) == 10
    
    # Check monotonicity
    for i in range(1, len(history)):
        assert history[i] <= history[i-1]
