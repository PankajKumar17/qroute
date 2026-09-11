"""
Phase 10: Full Benchmark Suite Execution
Master script to execute Q-Route against baseline algorithms.
"""
import argparse
import time
import numpy as np
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.ortools_baseline import ortools_solve, exact_solve_small
from qroute.algorithms.genetic_algorithm import genetic_algorithm
from qroute.algorithms.standard_pso import standard_pso
from qroute.algorithms.adaptive_pso import adaptive_pso
from qroute.algorithms.canonical_qpso import canonical_qpso
from qroute.robustness.scenario_testing import generate_fixed_scenarios, evaluate_route_robustness

def main():
    parser = argparse.ArgumentParser(description="Q-Route Benchmark Suite")
    parser.add_argument("--customers", type=int, default=10, help="Number of customers")
    parser.add_argument("--capacity", type=float, default=50.0, help="Vehicle capacity")
    parser.add_argument("--depart", type=float, default=0.0, help="Departure time")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    
    np.random.seed(args.seed)
    print(f"Building synthetic graph with {args.customers} customers...")
    G = build_synthetic_graph(args.customers + 1, seed=args.seed)
    demands = [np.random.randint(5, 15) for _ in range(args.customers)]
    
    results = []
    
    # 1. OR-Tools
    t0 = time.perf_counter()
    ort_cost, _ = ortools_solve(G, demands, args.capacity, args.depart)
    t1 = time.perf_counter()
    results.append(("OR-Tools", ort_cost, t1 - t0))
    
    # 2. GA
    t0 = time.perf_counter()
    ga_cost, _, _ = genetic_algorithm(G, demands, args.capacity, iterations=50, depart_time=args.depart)
    t1 = time.perf_counter()
    results.append(("Genetic Algorithm", ga_cost, t1 - t0))
    
    # 3. Standard PSO
    t0 = time.perf_counter()
    spso_cost, _, _ = standard_pso(G, demands, args.capacity, iterations=50, depart_time=args.depart)
    t1 = time.perf_counter()
    results.append(("Standard PSO", spso_cost, t1 - t0))
    
    # 4. Canonical QPSO
    t0 = time.perf_counter()
    cqpso_cost, _, _ = canonical_qpso(G, demands, args.capacity, iterations=50, depart_time=args.depart)
    t1 = time.perf_counter()
    results.append(("Canonical QPSO", cqpso_cost, t1 - t0))
    
    # 5. Q-Route (Adaptive PSO with QW)
    t0 = time.perf_counter()
    qr_cost, qr_routes, _, _ = adaptive_pso(G, demands, args.capacity, iterations=50, depart_time=args.depart)
    t1 = time.perf_counter()
    results.append(("Q-Route (Adaptive)", qr_cost, t1 - t0))
    
    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    print(f"{'Algorithm':<20} | {'Final Cost':<12} | {'Time (s)':<10}")
    print("-" * 50)
    for name, cost, t in results:
        print(f"{name:<20} | {cost:<12.2f} | {t:<10.3f}")
        
    print("\nRobustness Evaluation for Q-Route:")
    scenarios = generate_fixed_scenarios(G)
    # Evaluate robustness for the first route of the Q-Route solution
    if qr_routes:
        r = [0] + [c+1 for c in qr_routes[0]] + [0]
        rob = evaluate_route_robustness(G, r, args.depart, scenarios)
        print(f"  Lambda Score (L=0.5): {rob['lambda_score']:.2f}")
        print(f"  Worst Case Delay    : {rob['worst']:.2f}")

if __name__ == "__main__":
    main()
