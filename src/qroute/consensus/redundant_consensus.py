import numpy as np
from typing import List, Any
from qroute.algorithms.adaptive_pso import adaptive_pso

def route_similarity(routes_a: List[List[int]], routes_b: List[List[int]]) -> float:
    """
    Computes similarity between two solutions based on edge-overlap ratio.
    """
    def extract_edges(routes):
        edges = set()
        for r in routes:
            if not r: continue
            # Depot to first
            edges.add((0, r[0]))
            for i in range(len(r) - 1):
                edges.add((r[i], r[i+1]))
            # Last to depot
            edges.add((r[-1], 0))
        return edges
        
    edges_a = extract_edges(routes_a)
    edges_b = extract_edges(routes_b)
    
    if not edges_a and not edges_b:
        return 1.0
        
    overlap = edges_a.intersection(edges_b)
    union = edges_a.union(edges_b)
    
    return len(overlap) / len(union)

def run_subswarms(graph, demands: List[float], vehicle_capacity: float,
                  k_subswarms: int, iterations_per_window: int) -> List[List[List[int]]]:
    """
    Runs k independent AdaptivePSO sub-swarms for a window of iterations.
    """
    local_bests = []
    for _ in range(k_subswarms):
        # We don't care about the fitness/history/logs here, just the final routes
        _, best_routes, _, _ = adaptive_pso(
            graph, demands, vehicle_capacity,
            swarm_size=20, iterations=iterations_per_window
        )
        local_bests.append(best_routes)
        
    return local_bests

def check_consensus(local_bests: List[List[List[int]]], 
                    similarity_threshold: float = 0.8, 
                    redundancy_threshold: int = None) -> List[List[int]]:
    """
    Clustering local-best routes by similarity.
    Returns the largest cluster's representative if its size >= redundancy_threshold.
    """
    if not local_bests:
        return None
        
    k = len(local_bests)
    if redundancy_threshold is None:
        redundancy_threshold = int(np.ceil(k / 2))
        
    # Simple clustering: each solution forms a cluster of anything similar to it
    best_cluster_size = 0
    best_representative = None
    
    for i in range(k):
        cluster_size = 1
        for j in range(k):
            if i != j:
                sim = route_similarity(local_bests[i], local_bests[j])
                if sim >= similarity_threshold:
                    cluster_size += 1
                    
        if cluster_size > best_cluster_size:
            best_cluster_size = cluster_size
            best_representative = local_bests[i]
            
    if best_cluster_size >= redundancy_threshold:
        return best_representative
    return None

def compute_redundancy_curve(local_bests: List[List[List[int]]], similarity_threshold: float = 0.8) -> List[int]:
    """
    Returns the max cluster size as a function of the number of sub-swarms considered (1 to k).
    """
    curve = []
    for n in range(1, len(local_bests) + 1):
        subset = local_bests[:n]
        best_cluster_size = 0
        for i in range(n):
            cluster_size = 1
            for j in range(n):
                if i != j:
                    sim = route_similarity(subset[i], subset[j])
                    if sim >= similarity_threshold:
                        cluster_size += 1
            if cluster_size > best_cluster_size:
                best_cluster_size = cluster_size
        curve.append(best_cluster_size)
    return curve
