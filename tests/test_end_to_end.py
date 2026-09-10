import pytest
import time
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.adaptive_pso import adaptive_pso
from qroute.consensus.redundant_consensus import run_subswarms, check_consensus
from qroute.robustness.scenario_testing import generate_traffic_scenarios, evaluate_route_robustness

def test_end_to_end_pipeline():
    start_time = time.time()
    
    n_nodes = 31 # 30 customers
    G = build_synthetic_graph(n_nodes, seed=123)
    
    n_customers = n_nodes - 1
    demands = list(np.random.randint(5, 20, size=n_customers))
    vehicle_capacity = 60
    
    # Run consensus
    local_bests = run_subswarms(G, demands, vehicle_capacity, k_subswarms=3, iterations_per_window=10)
    best_routes = check_consensus(local_bests, similarity_threshold=0.6, redundancy_threshold=1)
    
    if best_routes is None:
        best_routes = local_bests[0]
        
    # Evaluate robustness
    scenarios = generate_traffic_scenarios(G, 5)
    for route in best_routes:
        graph_route = [0] + [c + 1 for c in route] + [0]
        metrics = evaluate_route_robustness(G, graph_route, 0.0, scenarios)
        assert metrics['mean'] > 0
        assert metrics['cv'] >= 0
        
    # Verify feasibility
    flattened = [c for r in best_routes for c in r]
    assert set(flattened) == set(range(n_customers)), "Not all customers visited"
    assert len(flattened) == n_customers, "Duplicate customers"
    
    for r in best_routes:
        assert sum(demands[c] for c in r) <= vehicle_capacity, "Capacity exceeded"
        
    end_time = time.time()
    elapsed = end_time - start_time
    assert elapsed < 60, f"Pipeline took {elapsed:.2f} seconds (limit: 60s)"
