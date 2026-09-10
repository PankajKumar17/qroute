import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from qroute.graph.network import build_synthetic_graph

from qroute.algorithms.nearest_neighbor import nearest_neighbor_vrp
from qroute.algorithms.genetic_algorithm import genetic_algorithm
from qroute.algorithms.standard_pso import standard_pso
from qroute.algorithms.ortools_baseline import ortools_solve, exact_solve_small
from qroute.consensus.redundant_consensus import run_subswarms, check_consensus
from qroute.graph.fitness import time_dependent_route_cost

def run_adaptive_consensus(graph, demands, vehicle_capacity, depart_time=0.0):
    # Runs consensus and evaluates representative
    local_bests = run_subswarms(graph, demands, vehicle_capacity, k_subswarms=5, iterations_per_window=30)
    rep = check_consensus(local_bests, similarity_threshold=0.7)
    if rep is None:
        rep = local_bests[0] # Fallback
        
    total_cost = 0.0
    for r in rep:
        graph_route = [0] + [c + 1 for c in r] + [0]
        cost, _ = time_dependent_route_cost(graph, graph_route, depart_time)
        total_cost += cost
    return total_cost

def full_comparison():
    sizes = [10, 20, 50] # 10 is small enough for exact
    seeds = 5 # Reduced seeds for faster execution (should be >=20 for real paper)
    vehicle_capacity = 50
    depart_time = 0.0
    
    results = []
    
    # For convergence plot tracking
    target_size_for_plot = 20
    convergence_data = {'PSO': [], 'GA': []}
    
    for n_nodes in sizes:
        n_customers = n_nodes - 1
        print(f"\nEvaluating Size: {n_customers} customers")
        
        for seed in range(seeds):
            G = build_synthetic_graph(n_nodes, seed=seed)
            np.random.seed(seed)
            demands = list(np.random.randint(5, 20, size=n_customers))
            
            # Exact
            exact_cost = None
            if n_customers <= 12:
                exact_cost, _ = exact_solve_small(G, demands, vehicle_capacity, depart_time)
                
            # OR-Tools
            t0 = time.time()
            ort_cost, _ = ortools_solve(G, demands, vehicle_capacity, depart_time)
            t_ort = time.time() - t0
            
            # Nearest Neighbor
            t0 = time.time()
            nn_routes = nearest_neighbor_vrp(G, demands, vehicle_capacity, depart_time)
            nn_cost = sum(time_dependent_route_cost(G, [0]+[c+1 for c in r]+[0], depart_time)[0] for r in nn_routes)
            t_nn = time.time() - t0
            
            # Standard PSO
            t0 = time.time()
            pso_cost, _, pso_hist = standard_pso(G, demands, vehicle_capacity, iterations=50)
            t_pso = time.time() - t0
            
            if n_nodes == target_size_for_plot:
                convergence_data['PSO'].append(pso_hist)
                
            # GA
            t0 = time.time()
            ga_cost, _, ga_hist = genetic_algorithm(G, demands, vehicle_capacity, iterations=50)
            t_ga = time.time() - t0
            
            if n_nodes == target_size_for_plot:
                convergence_data['GA'].append(ga_hist)
                
            # Adaptive Consensus
            t0 = time.time()
            ac_cost = run_adaptive_consensus(G, demands, vehicle_capacity, depart_time)
            t_ac = time.time() - t0
            
            res = {
                'size': n_customers,
                'seed': seed,
                'exact': exact_cost,
                'ortools': ort_cost,
                'time_ortools': t_ort,
                'nn': nn_cost,
                'time_nn': t_nn,
                'pso': pso_cost,
                'time_pso': t_pso,
                'ga': ga_cost,
                'time_ga': t_ga,
                'adaptive_consensus': ac_cost,
                'time_ac': t_ac
            }
            results.append(res)
            
    df = pd.DataFrame(results)
    
    # Save CSV
    import os
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/full_comparison.csv", index=False)
    
    # Summary Table
    summary = df.groupby('size').agg({
        'ortools': ['mean', 'std'],
        'time_ortools': 'mean',
        'nn': ['mean', 'std'],
        'pso': ['mean', 'std'],
        'ga': ['mean', 'std'],
        'adaptive_consensus': ['mean', 'std']
    })
    print("\n--- Summary ---")
    print(summary)
    
    # Optimality gap
    small_df = df[df['size'] <= 12]
    if not small_df.empty:
        print("\n--- Optimality Gaps (%) ---")
        for algo in ['ortools', 'nn', 'pso', 'ga', 'adaptive_consensus']:
            gap = (small_df[algo] - small_df['exact']) / small_df['exact'] * 100
            print(f"{algo}: {gap.mean():.2f}%")
            
    # Plot Convergence
    if convergence_data['PSO']:
        pso_arr = np.array(convergence_data['PSO'])
        ga_arr = np.array(convergence_data['GA'])
        
        plt.figure(figsize=(10, 6))
        
        for name, arr, color in [('PSO', pso_arr, 'blue'), ('GA', ga_arr, 'orange')]:
            mean = np.mean(arr, axis=0)
            std = np.std(arr, axis=0)
            iters = np.arange(len(mean))
            
            plt.plot(iters, mean, label=name, color=color)
            plt.fill_between(iters, mean - std, mean + std, alpha=0.2, color=color)
            
        plt.title("Convergence Comparison (Size 20)")
        plt.xlabel("Iteration")
        plt.ylabel("Fitness (Cost)")
        plt.legend()
        plt.savefig("data/convergence_plot.png")
        print("\nPlot saved to data/convergence_plot.png")

if __name__ == "__main__":
    full_comparison()
