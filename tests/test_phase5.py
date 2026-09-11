import pytest
import numpy as np
from qroute.consensus.redundant_consensus import darwinism_consensus
from qroute.graph.network import build_synthetic_graph

def test_phase5_verification(capsys):
    print("\n--- Phase 5 Verification ---")
    
    n_customers = 20
    np.random.seed(42)
    G = build_synthetic_graph(n_nodes=n_customers + 1, seed=42)
    demands = [np.random.randint(5, 15) for _ in range(n_customers)]
    capacity = 50.0
    
    k_subswarms = 5
    
    final_cost, final_routes, promoted_edges, edge_counts = darwinism_consensus(
        graph=G, demands=demands, vehicle_capacity=capacity,
        k_subswarms=k_subswarms, iterations_per_window=10
    )
    
    print(f"Total Edges Discovered Across {k_subswarms} Sub-swarms: {len(edge_counts)}")
    
    # Sort and show top 5 edges
    sorted_edges = sorted(edge_counts.items(), key=lambda x: x[1], reverse=True)
    print("Top 5 Edge Frequencies:")
    for edge, count in sorted_edges[:5]:
        print(f"  Edge {edge}: {count} / {k_subswarms} swarms")
        
    print(f"\nNumber of Promoted Edges (>= ceil(K/2)): {len(promoted_edges)}")
    print(f"Final True Consensus Fitness: {final_cost:.2f}")
    
    assert len(promoted_edges) > 0, "Expected at least some edges to be promoted in a complete graph with 5 subswarms"
