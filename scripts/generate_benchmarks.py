import json
import os
import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from qroute.graph.network import build_synthetic_graph
from qroute.algorithms.standard_pso import standard_pso
from qroute.algorithms.canonical_qpso import canonical_qpso
from qroute.algorithms.gaqpso import gaqpso
from qroute.algorithms.adaptive_pso import adaptive_pso
from qroute.consensus.redundant_consensus import extract_edges

def run_benchmarks():
    print("Generating Benchmark Data for Dashboard...")
    
    # 1. Setup small instance
    print("Setting up graph...")
    n_customers = 15
    vehicle_capacity = 50
    G = build_synthetic_graph(n_customers + 1, seed=42)
    demands = [10] * n_customers
    
    swarm_size = 20
    iterations = 50
    
    # 2. Convergence Comparison
    print("Running Convergence Benchmark (Standard PSO)...")
    _, _, std_hist, std_div = standard_pso(G, demands, vehicle_capacity, swarm_size, iterations)
    
    print("Running Convergence Benchmark (Canonical QPSO)...")
    _, _, qpso_hist, qpso_div = canonical_qpso(G, demands, vehicle_capacity, swarm_size, iterations)
    
    print("Running Convergence Benchmark (GAQPSO)...")
    _, _, gaqpso_hist, gaqpso_div = gaqpso(G, demands, vehicle_capacity, swarm_size, iterations)
    
    print("Running Convergence Benchmark (Q-Route / Adaptive PSO)...")
    _, _, qroute_hist, _, qroute_div = adaptive_pso(G, demands, vehicle_capacity, swarm_size, iterations, use_qw=True)
    
    # Format for Recharts
    convergence_data = []
    diversity_data = []
    
    for i in range(iterations):
        convergence_data.append({
            "iteration": i + 1,
            "Standard PSO": std_hist[i],
            "Canonical QPSO": qpso_hist[i],
            "GAQPSO": gaqpso_hist[i],
            "Q-Route": qroute_hist[i]
        })
        
        diversity_data.append({
            "iteration": i + 1,
            "Standard PSO": max(std_div[i], 1e-20),
            "Canonical QPSO": max(qpso_div[i], 1e-20),
            "GAQPSO": max(gaqpso_div[i], 1e-20),
            "Q-Route": max(qroute_div[i], 1e-20)
        })
        
    # 3. Redundancy / Consensus Benchmark
    print("Running Redundancy Benchmark (K=2 to 8)...")
    redundancy_data = []
    
    for k in range(2, 9):
        print(f"  Testing K={k} subswarms...")
        # Run K independent swarms manually to measure agreement
        edge_counts = {}
        for i in range(k):
            _, best_routes, _, _, _ = adaptive_pso(
                G, demands, vehicle_capacity,
                swarm_size=15, iterations=30
            )
            edges = extract_edges(best_routes)
            for e in edges:
                edge_counts[e] = edge_counts.get(e, 0) + 1
                
        # Calculate R: average agreement count of the top edges (a proxy for redundancy)
        if edge_counts:
            # Look at edges that appeared in at least 2 swarms to filter noise
            meaningful_edges = [c for c in edge_counts.values() if c >= 2]
            avg_redundancy = sum(meaningful_edges) / len(meaningful_edges) if meaningful_edges else 1.0
        else:
            avg_redundancy = 0
            
        redundancy_data.append({
            "subswarms": k,
            "redundancy": round(avg_redundancy, 2),
            "threshold": int(np.ceil(k / 2.0))
        })
        
    # 4. Save to Frontend Assets
    out_dir = Path(__file__).parent.parent / 'frontend' / 'src' / 'assets'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = out_dir / 'benchmark_data.json'
    with open(out_file, 'w') as f:
        json.dump({
            "convergence": convergence_data,
            "diversity": diversity_data,
            "redundancy": redundancy_data
        }, f, indent=2)
        
    print(f"Saved benchmark data to {out_file}")

if __name__ == "__main__":
    run_benchmarks()
