"""
This module implements a Darwinism-inspired heuristic consensus layer.
NOTE: This is a Darwinism-inspired heuristic consensus, NOT physical Quantum Darwinism.
"""
import numpy as np
from typing import List, Tuple
from qroute.algorithms.adaptive_pso import adaptive_pso

def extract_edges(routes: List[List[int]]) -> set:
    """Extracts all directed edges (including depot connections) from a set of routes."""
    edges = set()
    for r in routes:
        if not r: continue
        # Depot (0) to first customer
        edges.add((0, r[0] + 1))
        for i in range(len(r) - 1):
            edges.add((r[i] + 1, r[i+1] + 1))
        # Last customer to Depot (0)
        edges.add((r[-1] + 1, 0))
    return edges

def darwinism_consensus(graph, demands: List[float], vehicle_capacity: float, 
                        k_subswarms: int = 5, iterations_per_window: int = 20,
                        discount_factor: float = 0.01) -> Tuple[float, List[List[int]], List[Tuple[int, int]], dict, List[float]]:
    """
    Runs K independent swarms. Counts edge frequencies across their gbest routes.
    Promotes edges that appear in >= ceil(K/2) swarms.
    Runs a final consensus swarm where promoted edges are heavily discounted.
    """
    edge_counts = {}
    best_history = []
    min_cost = float('inf')
    
    # 1. Run K independent subswarms
    for i in range(k_subswarms):
        cost, best_routes, history, _ = adaptive_pso(
            graph, demands, vehicle_capacity,
            swarm_size=20, iterations=iterations_per_window
        )
        if cost < min_cost:
            min_cost = cost
            best_history = history
            
        edges = extract_edges(best_routes)
        for e in edges:
            edge_counts[e] = edge_counts.get(e, 0) + 1
            
    # 2. Promotion threshold R >= ceil(K/2)
    threshold = int(np.ceil(k_subswarms / 2.0))
    promoted_edges = [e for e, count in edge_counts.items() if count >= threshold]
    
    # 3. Discount promoted edges in a copy of the graph
    consensus_graph = graph.copy()
    for u, v in promoted_edges:
        if consensus_graph.is_multigraph():
            for key in consensus_graph[u][v]:
                consensus_graph[u][v][key]['travel_time'] *= discount_factor
                consensus_graph[u][v][key]['length'] *= discount_factor
        else:
            consensus_graph[u][v]['travel_time'] *= discount_factor
            consensus_graph[u][v]['length'] *= discount_factor
            
    # 4. Final consensus run
    _, final_routes, _, _ = adaptive_pso(
        consensus_graph, demands, vehicle_capacity,
        swarm_size=20, iterations=iterations_per_window
    )
    
    # 5. Re-evaluate true cost on the original unmodified graph
    from qroute.graph.fitness import time_dependent_route_cost
    true_cost = 0.0
    for r in final_routes:
        graph_route = [0] + [c + 1 for c in r] + [0]
        cost, _ = time_dependent_route_cost(graph, graph_route, depart_time=0.0)
        true_cost += cost
        
    if best_history and true_cost < min_cost:
        best_history.append(true_cost)
    elif best_history:
        best_history.append(best_history[-1])
        
    return true_cost, final_routes, promoted_edges, edge_counts, best_history
