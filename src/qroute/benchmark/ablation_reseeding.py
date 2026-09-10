import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.standard_pso import standard_pso
from qroute.algorithms.adaptive_pso import adaptive_pso

def run_ablation():
    n_nodes = 30
    swarm_size = 20
    iterations = 50
    n_seeds = 20
    vehicle_capacity = 50
    
    results = []
    
    for seed in range(n_seeds):
        G = build_synthetic_graph(n_nodes, seed=seed)
        n_customers = n_nodes - 1
        np.random.seed(seed)
        demands = list(np.random.randint(5, 20, size=n_customers))
        
        # (a) Standard PSO
        fit_a, _, hist_a = standard_pso(G, demands, vehicle_capacity, swarm_size, iterations)
        
        # (b) PSO + Uniform Random Reseeding (We can simulate this using adaptive_pso but hacking quantum_walk_sample)
        # We will create a local wrapper for the test
        from qroute.encoding.random_key import encode_particle
        from qroute.algorithms import adaptive_pso as apso_module
        
        # Monkey patch quantum_walk_sample to return uniform random
        original_qws = apso_module.quantum_walk_sample
        apso_module.quantum_walk_sample = lambda g, n, s=None: [encode_particle(n_customers) for _ in range(n)]
        
        fit_b, _, hist_b, log_b = apso_module.adaptive_pso(
            G, demands, vehicle_capacity, swarm_size, iterations,
            w_stagnation=5, epsilon=0.1, d_min=1.0
        )
        
        # Restore monkey patch
        apso_module.quantum_walk_sample = original_qws
        
        # (c) AdaptivePSO with Quantum-Walk Reseeding
        fit_c, _, hist_c, log_c = apso_module.adaptive_pso(
            G, demands, vehicle_capacity, swarm_size, iterations,
            w_stagnation=5, epsilon=0.1, d_min=1.0
        )
        
        results.append({
            'seed': seed,
            'fitness_std_pso': fit_a,
            'fitness_rand_reseed': fit_b,
            'fitness_qw_reseed': fit_c,
            'recovers_rand': len(log_b),
            'recovers_qw': len(log_c)
        })
        
    df = pd.DataFrame(results)
    df.to_csv("data/ablation_results.csv", index=False)
    
    print("\n--- Ablation Results (Mean +/- Std) ---")
    print(f"Standard PSO:    {df['fitness_std_pso'].mean():.2f} +/- {df['fitness_std_pso'].std():.2f}")
    print(f"Random Reseed:   {df['fitness_rand_reseed'].mean():.2f} +/- {df['fitness_rand_reseed'].std():.2f}")
    print(f"Quantum Reseed:  {df['fitness_qw_reseed'].mean():.2f} +/- {df['fitness_qw_reseed'].std():.2f}")
    
    # Mann-Whitney U test
    stat_c_a, p_c_a = mannwhitneyu(df['fitness_qw_reseed'], df['fitness_std_pso'], alternative='less')
    stat_c_b, p_c_b = mannwhitneyu(df['fitness_qw_reseed'], df['fitness_rand_reseed'], alternative='less')
    
    print("\n--- Statistical Significance (p-values for C < A and C < B) ---")
    print(f"Quantum Reseed better than Standard PSO: p = {p_c_a:.4f}")
    print(f"Quantum Reseed better than Random Reseed: p = {p_c_b:.4f}")

if __name__ == "__main__":
    run_ablation()
