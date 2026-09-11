"""
This module implements robustness testing via fixed traffic-shock scenarios.
NOTE: This is heuristic robustness testing for practical demonstration, 
NOT a formal mathematical worst-case bounding proof.
"""
import numpy as np
from typing import List, Tuple, Dict
from qroute.graph.traffic import edge_travel_time
from qroute.graph.fitness import time_dependent_route_cost

def generate_fixed_scenarios(graph) -> Dict[str, Dict[Tuple[int, int], float]]:
    """
    Generates 4 fixed scenarios: Base Case, Minor Shock, Extreme Shock, Correlated Shock.
    """
    scenarios = {
        "Base Case": {},
        "Minor Shock": {},
        "Extreme Shock": {},
        "Correlated Shock": {}
    }
    
    edges = list(graph.edges())
    if not edges: return scenarios
    
    np.random.seed(42) # fixed for reproducibility
    
    # Minor: 1.5x delay on ~10% edges
    minor_edges = [edges[i] for i in np.random.choice(len(edges), max(1, len(edges)//10), replace=False)]
    for e in minor_edges:
        scenarios["Minor Shock"][e] = 1.5
        
    # Extreme: 3.0x delay on ~50% edges
    extreme_edges = [edges[i] for i in np.random.choice(len(edges), max(1, len(edges)//2), replace=False)]
    for e in extreme_edges:
        scenarios["Extreme Shock"][e] = 3.0
        
    # Correlated: Spatially contiguous bottleneck. Pick a random node, affect all incident edges.
    bottleneck_node = np.random.choice(list(graph.nodes()))
    for u, v in edges:
        if u == bottleneck_node or v == bottleneck_node:
            scenarios["Correlated Shock"][(u, v)] = 4.0
            
    return scenarios

def evaluate_route_scenario(graph, route: List[int], depart_time: float, scenario: Dict[Tuple[int, int], float]) -> float:
    if len(route) < 2:
        return 0.0
        
    current_time = depart_time
    total_cost = 0.0
    
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        
        # We compute the standard composite cost...
        # Wait, the easiest way to inject the shock is to temporarily multiply the edge travel time.
        # But we must simulate the recursive arrival times accurately.
        
        # Fast path: we use edge_travel_time directly, apply shock, 
        # and assume alpha=1.0, beta=0, gamma=0 for the robustness evaluation (or we can use full).
        # Let's use simple time cost for robustness.
        tt = edge_travel_time(graph, u, v, current_time)
        shock = scenario.get((u, v), 1.0)
        tt *= shock
        
        total_cost += tt
        current_time += tt
        
    return total_cost

def risk_aware_score(costs: List[float], lambd: float = 0.5) -> float:
    """
    Selection rule: λ * C_worst + (1 - λ) * C_avg
    """
    if not costs: return 0.0
    c_worst = np.max(costs)
    c_avg = np.mean(costs)
    return lambd * c_worst + (1.0 - lambd) * c_avg

def evaluate_route_robustness(graph, route: List[int], depart_time: float, scenarios: Dict[str, Dict]) -> dict:
    results = {}
    costs = []
    
    for name, scenario in scenarios.items():
        c = evaluate_route_scenario(graph, route, depart_time, scenario)
        results[name] = c
        costs.append(c)
        
    results['avg'] = np.mean(costs)
    results['worst'] = np.max(costs)
    results['lambda_score'] = risk_aware_score(costs, lambd=0.5)
    
    return results
