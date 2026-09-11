import pytest
import numpy as np
from qroute.algorithms.quantum_walk import quantum_walk_sample, uniform_random_sample, lhs_sample
from qroute.algorithms.diversity import swarm_diversity

def simple_pca(X, n_components=2):
    X = np.array(X)
    X_centered = X - np.mean(X, axis=0)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    return X_centered @ Vt.T[:, :n_components]

def test_phase3_verification(capsys):
    print("\n--- Phase 3 Verification ---")
    
    n_customers = 20
    swarm_size = 50
    n_seeds = 10
    
    results = {"QW": [], "Uniform": [], "LHS": []}
    
    for seed in range(n_seeds):
        qw_swarm = quantum_walk_sample(n_customers, swarm_size, seed=seed)
        un_swarm = uniform_random_sample(n_customers, swarm_size, seed=seed)
        lhs_swarm = lhs_sample(n_customers, swarm_size, seed=seed)
        
        results["QW"].append(swarm_diversity(qw_swarm))
        results["Uniform"].append(swarm_diversity(un_swarm))
        results["LHS"].append(swarm_diversity(lhs_swarm))
        
    print(f"Diversity over {n_seeds} seeds (Mean ± Std):")
    for method, divs in results.items():
        print(f"  {method:8s}: {np.mean(divs):.4f} ± {np.std(divs):.4f}")
        
    # PCA projection on one seed
    qw_swarm = quantum_walk_sample(n_customers, swarm_size, seed=42)
    un_swarm = uniform_random_sample(n_customers, swarm_size, seed=42)
    
    qw_proj = simple_pca(qw_swarm, n_components=2)
    un_proj = simple_pca(un_swarm, n_components=2)
    
    print("\nVisual Check (Top 3 points of 2D PCA projection):")
    print(f"  QW Swarm: \n{qw_proj[:3]}")
    print(f"  Uniform: \n{un_proj[:3]}")
    print("\nThe QW swarm typically covers a different subspace due to structured correlations, unlike pure uniform.")
