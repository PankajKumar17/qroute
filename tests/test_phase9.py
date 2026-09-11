import pytest
import time
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.standard_pso import standard_pso
from qroute.algorithms.adaptive_pso import adaptive_pso

def get_convergence_iter(history, threshold=1e-3):
    # Returns the iteration where fitness no longer improved by > threshold
    if not history: return 0
    best = history[0]
    best_iter = 0
    for i, fit in enumerate(history):
        if best - fit > threshold:
            best = fit
            best_iter = i
    return best_iter

def test_phase9_verification(capsys):
    print("\n--- Phase 9: Ablation Ladder ---")
    
    n_customers = 15
    np.random.seed(42)
    G = build_synthetic_graph(n_nodes=n_customers + 1, seed=42)
    demands = [np.random.randint(5, 15) for _ in range(n_customers)]
    capacity = 50.0
    
    results = []
    
    # 1. Standard PSO
    np.random.seed(42)
    t0 = time.perf_counter()
    std_cost, _, std_hist = standard_pso(G, demands, capacity, swarm_size=20, iterations=50)
    t1 = time.perf_counter()
    results.append(("Standard PSO", std_cost, get_convergence_iter(std_hist), t1-t0))
    
    # 2. Adaptive PSO (Random Reseeding, No QW)
    np.random.seed(42)
    t0 = time.perf_counter()
    apso_cost, _, apso_hist, _ = adaptive_pso(G, demands, capacity, swarm_size=20, iterations=50, use_qw=False)
    t1 = time.perf_counter()
    results.append(("Adaptive (No QW)", apso_cost, get_convergence_iter(apso_hist), t1-t0))
    
    # 3. Q-Route (QW Reseeding)
    np.random.seed(42)
    t0 = time.perf_counter()
    qr_cost, _, qr_hist, _ = adaptive_pso(G, demands, capacity, swarm_size=20, iterations=50, use_qw=True)
    t1 = time.perf_counter()
    results.append(("Q-Route (QW)", qr_cost, get_convergence_iter(qr_hist), t1-t0))
    
    print(f"\n{'Algorithm':<20} | {'Final Fitness':<15} | {'Conv. Iteration':<18} | {'Time (s)':<10}")
    print("-" * 75)
    for name, cost, c_iter, t in results:
        print(f"{name:<20} | {cost:<15.2f} | {c_iter:<18} | {t:<10.3f}")
        
    assert qr_cost > 0
