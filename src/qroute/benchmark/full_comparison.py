import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from qroute.graph.network import build_synthetic_graph

from qroute.algorithms.nearest_neighbor import nearest_neighbor_vrp
from qroute.algorithms.genetic_algorithm import genetic_algorithm
from qroute.algorithms.standard_pso import standard_pso
from qroute.algorithms.canonical_qpso import canonical_qpso
from qroute.algorithms.gaqpso import gaqpso
from qroute.algorithms.ortools_baseline import ortools_solve, exact_solve_small
from qroute.consensus.redundant_consensus import darwinism_consensus
from qroute.graph.fitness import time_dependent_route_cost

def run_adaptive_consensus(graph, demands, vehicle_capacity, depart_time=0.0):
    cost, routes, _, _, _ = darwinism_consensus(graph, demands, vehicle_capacity, k_subswarms=5, iterations_per_window=30)
    return cost, routes, None, None, None

def get_iters_to_threshold(history, threshold):
    if not history: return 0
    for i, cost in enumerate(history):
        if cost <= threshold:
            return i + 1
    return len(history)

def full_comparison():
    sizes = [10, 20, 50] # 10 is small enough for exact
    seeds = 5 # Reduced seeds for faster execution (should be >=20 for real paper)
    vehicle_capacity = 50
    depart_time = 0.0
    iterations = 50
    
    results = []
    
    # For convergence plot tracking
    target_size_for_plot = 20
    convergence_data = {'PSO': [], 'GA': [], 'QPSO': [], 'GAQPSO': []}
    diversity_data = {'QPSO': [], 'GAQPSO': []}
    
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
            ort_cost, ort_routes = ortools_solve(G, demands, vehicle_capacity, depart_time)
            t_ort = time.time() - t0
            ort_vehicles = len(ort_routes) if ort_routes else 0
            
            threshold_cost = ort_cost * 1.05 if ort_cost else float('inf')
            
            # Nearest Neighbor
            t0 = time.time()
            nn_routes = nearest_neighbor_vrp(G, demands, vehicle_capacity, depart_time)
            nn_cost = sum(time_dependent_route_cost(G, [0]+[c+1 for c in r]+[0], depart_time)[0] for r in nn_routes)
            t_nn = time.time() - t0
            nn_vehicles = len(nn_routes)
            
            # Standard PSO
            t0 = time.time()
            pso_cost, pso_routes, pso_hist, pso_div = standard_pso(G, demands, vehicle_capacity, iterations=iterations)
            t_pso = time.time() - t0
            
            if n_nodes == target_size_for_plot:
                convergence_data['PSO'].append(pso_hist)
                
            # GA
            t0 = time.time()
            ga_cost, ga_routes, ga_hist = genetic_algorithm(G, demands, vehicle_capacity, iterations=iterations)
            t_ga = time.time() - t0
            
            if n_nodes == target_size_for_plot:
                convergence_data['GA'].append(ga_hist)
                
            # QPSO
            t0 = time.time()
            qpso_cost, qpso_routes, qpso_hist, qpso_div = canonical_qpso(G, demands, vehicle_capacity, iterations=iterations)
            t_qpso = time.time() - t0
            
            if n_nodes == target_size_for_plot:
                convergence_data['QPSO'].append(qpso_hist)
                diversity_data['QPSO'].append(qpso_div)
                
            # GAQPSO
            t0 = time.time()
            gaqpso_cost, gaqpso_routes, gaqpso_hist, gaqpso_div = gaqpso(G, demands, vehicle_capacity, iterations=iterations)
            t_gaqpso = time.time() - t0
            
            if n_nodes == target_size_for_plot:
                convergence_data['GAQPSO'].append(gaqpso_hist)
                diversity_data['GAQPSO'].append(gaqpso_div)
                
            # Adaptive Consensus
            t0 = time.time()
            ac_cost, ac_routes, _, _, _ = run_adaptive_consensus(G, demands, vehicle_capacity, depart_time)
            t_ac = time.time() - t0
            
            res = {
                'size': n_customers,
                'seed': seed,
                'exact': exact_cost,
                'ortools': ort_cost,
                'time_ortools': t_ort,
                'vehicles_ortools': ort_vehicles,
                
                'nn': nn_cost,
                'time_nn': t_nn,
                'vehicles_nn': nn_vehicles,
                
                'pso': pso_cost,
                'time_pso': t_pso,
                'time_per_iter_pso': t_pso / iterations,
                'vehicles_pso': len(pso_routes),
                'iters_to_5pct_pso': get_iters_to_threshold(pso_hist, threshold_cost),
                'success_pso': 1 if pso_cost <= threshold_cost else 0,
                
                'ga': ga_cost,
                'time_ga': t_ga,
                'time_per_iter_ga': t_ga / iterations,
                'vehicles_ga': len(ga_routes),
                'iters_to_5pct_ga': get_iters_to_threshold(ga_hist, threshold_cost),
                'success_ga': 1 if ga_cost <= threshold_cost else 0,
                
                'qpso': qpso_cost,
                'time_qpso': t_qpso,
                'time_per_iter_qpso': t_qpso / iterations,
                'vehicles_qpso': len(qpso_routes),
                'iters_to_5pct_qpso': get_iters_to_threshold(qpso_hist, threshold_cost),
                'success_qpso': 1 if qpso_cost <= threshold_cost else 0,
                
                'gaqpso': gaqpso_cost,
                'time_gaqpso': t_gaqpso,
                'time_per_iter_gaqpso': t_gaqpso / iterations,
                'vehicles_gaqpso': len(gaqpso_routes),
                'iters_to_5pct_gaqpso': get_iters_to_threshold(gaqpso_hist, threshold_cost),
                'success_gaqpso': 1 if gaqpso_cost <= threshold_cost else 0,
                
                'adaptive_consensus': ac_cost,
                'time_ac': t_ac,
                'vehicles_ac': len(ac_routes),
                'success_ac': 1 if ac_cost <= threshold_cost else 0
            }
            results.append(res)
            
    df = pd.DataFrame(results)
    
    # Save CSV
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/full_comparison.csv", index=False)
    
    # Summary Table with Min/Max
    summary = df.groupby('size').agg({
        'ortools': ['mean', 'min', 'max'],
        'time_ortools': 'mean',
        'nn': ['mean', 'min', 'max'],
        
        'pso': ['mean', 'min', 'max'],
        'time_per_iter_pso': 'mean',
        'iters_to_5pct_pso': 'mean',
        'success_pso': 'mean',
        
        'ga': ['mean', 'min', 'max'],
        'time_per_iter_ga': 'mean',
        'iters_to_5pct_ga': 'mean',
        'success_ga': 'mean',
        
        'qpso': ['mean', 'min', 'max'],
        'time_per_iter_qpso': 'mean',
        'iters_to_5pct_qpso': 'mean',
        'success_qpso': 'mean',
        
        'gaqpso': ['mean', 'min', 'max'],
        'time_per_iter_gaqpso': 'mean',
        'iters_to_5pct_gaqpso': 'mean',
        'success_gaqpso': 'mean',
        
        'adaptive_consensus': ['mean', 'min', 'max'],
        'success_ac': 'mean'
    })
    print("\n--- Summary ---")
    print(summary)
    
    # Optimality gap
    small_df = df[df['size'] <= 12]
    if not small_df.empty:
        print("\n--- Optimality Gaps (%) ---")
        for algo in ['ortools', 'nn', 'pso', 'ga', 'qpso', 'gaqpso', 'adaptive_consensus']:
            gap = (small_df[algo] - small_df['exact']) / small_df['exact'] * 100
            print(f"{algo}: {gap.mean():.2f}%")
            
    # Plot Convergence
    if convergence_data['PSO']:
        plt.figure(figsize=(10, 6))
        
        colors = {'PSO': 'blue', 'GA': 'orange', 'QPSO': 'green', 'GAQPSO': 'red'}
        
        for name in ['PSO', 'GA', 'QPSO', 'GAQPSO']:
            arr = np.array(convergence_data[name])
            mean = np.mean(arr, axis=0)
            std = np.std(arr, axis=0)
            iters = np.arange(len(mean))
            
            plt.plot(iters, mean, label=name, color=colors[name])
            plt.fill_between(iters, mean - std, mean + std, alpha=0.2, color=colors[name])
            
        plt.title("Convergence Comparison (Size 20)")
        plt.xlabel("Iteration")
        plt.ylabel("Fitness (Cost)")
        plt.legend()
        plt.savefig("data/convergence_plot.png")
        print("\nPlot saved to data/convergence_plot.png")
        
    # Plot Diversity (Log Scale as in paper)
    if diversity_data['QPSO']:
        plt.figure(figsize=(10, 6))
        
        for name, color in [('QPSO', 'green'), ('GAQPSO', 'red')]:
            arr = np.array(diversity_data[name])
            # Avoid log(0)
            arr = np.maximum(arr, 1e-20)
            mean = np.mean(np.log10(arr), axis=0)
            
            iters = np.arange(len(mean))
            plt.plot(iters, mean, label=name, color=color)
            
        plt.title("Diversity Comparison (Size 20)")
        plt.xlabel("Iteration")
        plt.ylabel("Log10(Diversity)")
        plt.legend()
        plt.savefig("data/diversity_plot.png")
        print("Plot saved to data/diversity_plot.png")

if __name__ == "__main__":
    full_comparison()
