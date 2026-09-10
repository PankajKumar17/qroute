import pytest
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.ortools_baseline import ortools_solve, exact_solve_small

def test_ortools_vs_exact():
    n_nodes = 7 # 6 customers + 1 depot
    G = build_synthetic_graph(n_nodes, seed=42)
    n_customers = n_nodes - 1
    
    demands = [10] * n_customers
    vehicle_capacity = 30
    
    heuristic_cost, _ = ortools_solve(G, demands, vehicle_capacity)
    exact_cost, _ = exact_solve_small(G, demands, vehicle_capacity)
    
    assert exact_cost > 0
    assert heuristic_cost >= exact_cost
