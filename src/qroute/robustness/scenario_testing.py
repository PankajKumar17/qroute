import numpy as np
from typing import List, Tuple, Dict
from qroute.graph.traffic import edge_travel_time

def generate_traffic_scenarios(graph, n_scenarios: int, shock_probability: float = 0.1, max_shock: float = 3.0) -> List[Dict[Tuple[int, int], float]]:
    """
    Generates scenarios. Each scenario is a dictionary mapping edge (u, v) to a shock multiplier.
    If an edge is not in the dictionary, its multiplier is 1.0.
    """
    scenarios = []
    edges = list(graph.edges())
    
    for _ in range(n_scenarios):
        scenario = {}
        for u, v in edges:
            if np.random.rand() < shock_probability:
                # Random shock between 1.0 and max_shock
                scenario[(u, v)] = np.random.uniform(1.0, max_shock)
        scenarios.append(scenario)
        
    return scenarios

def evaluate_route_scenario(graph, route: List[int], depart_time: float, scenario: Dict[Tuple[int, int], float]) -> float:
    if len(route) < 2:
        return 0.0
        
    current_time = depart_time
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        
        tt = edge_travel_time(graph, u, v, current_time)
        shock = scenario.get((u, v), 1.0)
        tt *= shock
        
        current_time += tt
        
    return current_time - depart_time

def evaluate_route_robustness(graph, route: List[int], depart_time: float, scenarios: List[Dict[Tuple[int, int], float]]) -> dict:
    costs = []
    for scenario in scenarios:
        costs.append(evaluate_route_scenario(graph, route, depart_time, scenario))
        
    mean = np.mean(costs)
    std = np.std(costs)
    cv = std / mean if mean > 0 else 0
    worst = np.max(costs)
    
    return {
        'mean': mean,
        'std': std,
        'cv': cv,
        'worst': worst
    }
