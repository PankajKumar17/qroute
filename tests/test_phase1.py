import pytest
import numpy as np
import networkx as nx
from qroute.graph.network import build_synthetic_graph
from qroute.graph.traffic import edge_travel_time
from qroute.graph.fitness import time_dependent_route_cost, PROFILES

def test_fifo_property():
    """
    Test that departing later must never produce an earlier arrival than departing earlier.
    """
    G = build_synthetic_graph(n_nodes=10, seed=42)
    # Pick a random edge
    edges = list(G.edges())
    u, v = edges[0]
    
    departures = np.linspace(0, 24 * 3600, 100)
    arrivals = []
    
    for d in departures:
        tt = edge_travel_time(G, u, v, arrival_time=d)
        arrivals.append(d + tt)
        
    for i in range(1, len(arrivals)):
        assert arrivals[i] >= arrivals[i-1], f"FIFO violated! Dep {departures[i-1]} -> Arr {arrivals[i-1]}, Dep {departures[i]} -> Arr {arrivals[i]}"
        
def test_dynamic_vs_static_cost(capsys):
    """
    Test that time-dependent sequential arrival cost differs from naive static-cost sum.
    """
    G = build_synthetic_graph(n_nodes=20, seed=42)
    # create a sequential route
    route = list(range(10)) 
    
    # Static cost sum (assuming departure = 8 AM for all edges independently to isolate static assumption vs dynamic accumulation)
    depart_time_8am = 8.0 * 3600
    static_cost_sum = 0.0
    for i in range(len(route) - 1):
        u, v = route[i], route[i+1]
        static_cost_sum += edge_travel_time(G, u, v, arrival_time=depart_time_8am) # Evaluated at static 8 AM
        
    # Dynamic sequential cost
    dynamic_cost, dynamic_time = time_dependent_route_cost(G, route, depart_time=depart_time_8am, profile="fastest")
    
    print("\n--- Phase 1 Verification ---")
    print(f"Static Cost Sum (always evaluated at t=0): {static_cost_sum:.2f}")
    print(f"Dynamic Sequential Cost (fastest profile): {dynamic_cost:.2f}")
    
    assert abs(static_cost_sum - dynamic_cost) > 1e-4, "Dynamic cost should differ from static cost due to traffic multipliers changing over time!"
    
    print("\nProfiles Configuration:")
    for name, weights in PROFILES.items():
        print(f" - {name.capitalize()}: alpha={weights['alpha']}, beta={weights['beta']}, gamma={weights['gamma']}")
        
    # Ensure they are distinct
    assert PROFILES["fastest"] != PROFILES["shortest"]
    assert PROFILES["fastest"] != PROFILES["balanced"]
    assert PROFILES["shortest"] != PROFILES["balanced"]
