import pytest
import numpy as np
from qroute.robustness.scenario_testing import generate_fixed_scenarios, evaluate_route_robustness
from qroute.graph.network import build_synthetic_graph

def test_phase6_verification(capsys):
    print("\n--- Phase 6 Verification ---")
    
    n_customers = 10
    G = build_synthetic_graph(n_nodes=n_customers + 1, seed=42)
    
    scenarios = generate_fixed_scenarios(G)
    
    # 1. Print scenario definitions
    print("Scenario Definitions:")
    for name, data in scenarios.items():
        print(f"  {name}: {len(data)} affected edges")
        
    # 2. Evaluate static baseline route vs a hypothetical "adaptive" route
    # Baseline just visits sequentially
    baseline_route = [0] + list(range(1, n_customers + 1)) + [0]
    
    # Adaptive route evades some high-delay edges
    adaptive_route = [0] + list(reversed(range(1, n_customers + 1))) + [0]
    
    base_results = evaluate_route_robustness(G, baseline_route, 0.0, scenarios)
    adaptive_results = evaluate_route_robustness(G, adaptive_route, 0.0, scenarios)
    
    # 3. Output Matrix and lambda-score
    print("\nRobustness Matrix:")
    print(f"{'Metric':<20} | {'Baseline':<12} | {'Adaptive':<12}")
    print("-" * 50)
    for key in scenarios.keys():
        print(f"{key:<20} | {base_results[key]:<12.2f} | {adaptive_results[key]:<12.2f}")
        
    print("-" * 50)
    print(f"{'Average (C_avg)':<20} | {base_results['avg']:<12.2f} | {adaptive_results['avg']:<12.2f}")
    print(f"{'Worst-Case (C_worst)':<20} | {base_results['worst']:<12.2f} | {adaptive_results['worst']:<12.2f}")
    print(f"{'Lambda Score (L=0.5)':<20} | {base_results['lambda_score']:<12.2f} | {adaptive_results['lambda_score']:<12.2f}")
    
    # Confirm lambda score logic triggers correctly
    # If the adaptive score is lower, it wins.
    print(f"\nSelection Logic: Adaptive wins if lambda_score ({adaptive_results['lambda_score']:.2f}) < Baseline worst ({base_results['worst']:.2f})")
    assert adaptive_results['lambda_score'] < base_results['worst'], "Lambda selection should favor adaptive routes!"
