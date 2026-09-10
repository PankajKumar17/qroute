import pytest
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.genetic_algorithm import genetic_algorithm

def test_genetic_algorithm():
    n_nodes = 10
    G = build_synthetic_graph(n_nodes, seed=42)
    n_customers = n_nodes - 1
    
    demands = [10] * n_customers
    vehicle_capacity = 30
    
    best_fitness, best_routes, history = genetic_algorithm(
        G, demands, vehicle_capacity, pop_size=10, iterations=10
    )
    
    assert best_fitness > 0
    assert len(history) == 10
    
    flattened = [c for r in best_routes for c in r]
    assert set(flattened) == set(range(n_customers))
