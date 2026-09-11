import pytest
import time
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.ortools_baseline import ortools_solve
from qroute.algorithms.genetic_algorithm import genetic_algorithm
from qroute.algorithms.canonical_qpso import canonical_qpso

def test_phase7_verification(capsys):
    print("\n--- Phase 7 Verification ---")
    
    n_customers = 8
    np.random.seed(42)
    G = build_synthetic_graph(n_nodes=n_customers + 1, seed=42)
    demands = [np.random.randint(5, 15) for _ in range(n_customers)]
    capacity = 50.0
    
    # Run OR-Tools
    t0 = time.perf_counter()
    ortools_cost, ortools_routes = ortools_solve(G, demands, capacity)
    t1 = time.perf_counter()
    print(f"OR-Tools      : Cost = {ortools_cost:<10.2f} | Time = {t1-t0:.4f}s")
    
    # Run GA
    t0 = time.perf_counter()
    ga_cost, ga_routes, _ = genetic_algorithm(G, demands, capacity, pop_size=20, iterations=30)
    t1 = time.perf_counter()
    print(f"Genetic Alg   : Cost = {ga_cost:<10.2f} | Time = {t1-t0:.4f}s")
    
    # Run Canonical QPSO
    t0 = time.perf_counter()
    qpso_cost, qpso_routes, _ = canonical_qpso(G, demands, capacity, swarm_size=20, iterations=30)
    t1 = time.perf_counter()
    print(f"Canonical QPSO: Cost = {qpso_cost:<10.2f} | Time = {t1-t0:.4f}s")
    
    assert ortools_cost > 0
    assert ga_cost > 0
    assert qpso_cost > 0
