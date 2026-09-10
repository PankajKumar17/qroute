import pytest
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.encoding.random_key import encode_particle, decode_to_tour
from qroute.encoding.split import split_giant_tour
from qroute.graph.fitness import time_dependent_route_cost

def test_integration_pipeline():
    n_nodes = 20
    # Create graph where nodes are 0..19.
    # We treat node 0 as depot, 1..19 as customers.
    G = build_synthetic_graph(n_nodes, seed=42)
    
    n_customers = n_nodes - 1
    # Demands for customers 1..19. Let's use 0..18 indices to represent them in the tour.
    demands = list(np.random.randint(5, 20, size=n_customers))
    vehicle_capacity = 50
    
    # Encode
    keys = encode_particle(n_customers, seed=42)
    # Decode
    tour = decode_to_tour(keys)
    
    # Split
    routes = split_giant_tour(tour, demands, vehicle_capacity)
    
    total_cost = 0.0
    for r in routes:
        # Map back to graph node indices (depot is 0, customers are +1)
        # We need a route starting at 0, visiting r, ending at 0.
        graph_route = [0] + [c + 1 for c in r] + [0]
        
        cost, _ = time_dependent_route_cost(G, graph_route, depart_time=8 * 3600)
        total_cost += cost
        
    assert total_cost > 0
    assert np.isfinite(total_cost)
