import pytest
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.ortools_baseline import exact_solve_small
from qroute.algorithms.adaptive_pso import adaptive_pso

def test_phase8_verification(capsys):
    print("\n--- Phase 8 Verification ---")
    
    n_customers = 10
    np.random.seed(42)
    G = build_synthetic_graph(n_nodes=n_customers + 1, seed=42)
    demands = [np.random.randint(5, 15) for _ in range(n_customers)]
    
    # Q-Route with Infinite Capacity (Shortest-Path Mode)
    q_cost, q_routes, _, _ = adaptive_pso(
        graph=G, demands=demands, vehicle_capacity=float('inf'),
        swarm_size=30, iterations=50
    )
    
    # Exact Shortest Path Tour (TSP via OR-Tools exact config)
    exact_cost, exact_routes = exact_solve_small(G, demands, vehicle_capacity=1000000)
    
    print(f"Exact TSP Cost : {exact_cost:.2f} | Route: {exact_routes}")
    print(f"Q-Route Cost   : {q_cost:.2f} | Route: {q_routes}")
    
    assert len(q_routes) == 1, "Infinite capacity mode must yield exactly 1 route!"
    
    gap = abs(q_cost - exact_cost) / exact_cost * 100
    print(f"\nGap: {gap:.2f}%")
