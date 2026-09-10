import pytest
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.adaptive_pso import adaptive_pso

def test_adaptive_pso_reseeding():
    # Very small search space to trigger stagnation quickly
    n_nodes = 5
    G = build_synthetic_graph(n_nodes, seed=42)
    n_customers = n_nodes - 1
    
    demands = [10] * n_customers
    vehicle_capacity = 30
    
    best_fitness, best_routes, history, reseed_log = adaptive_pso(
        G, demands, vehicle_capacity, swarm_size=5, iterations=20,
        w_stagnation=3, epsilon=0.1, d_min=1.0 # high d_min to force trigger
    )
    
    assert best_fitness > 0
    assert len(reseed_log) > 0
    
    # Check that diversity actually increased after reseed
    first_reseed = reseed_log[0]
    assert first_reseed['diversity_after'] > first_reseed['diversity_before']
