from typing import List, Tuple
from qroute.graph.traffic import edge_travel_time

PROFILES = {
    "fastest": {"alpha": 1.0, "beta": 0.0, "gamma": 0.0},
    "shortest": {"alpha": 0.0, "beta": 1.0, "gamma": 0.0},
    "balanced": {"alpha": 0.4, "beta": 0.4, "gamma": 0.2},
}

def time_dependent_route_cost(graph, route: List[int], depart_time: float, profile: str = "balanced") -> Tuple[float, float]:
    """
    Computes the total time-dependent cost for a sequential route, updating the current
    clock time at each node to fetch the time-dependent edge cost.
    
    Args:
        graph: NetworkX graph.
        route: A list of node IDs to visit in order.
        depart_time: Time (in seconds from midnight) when departing the first node.
        profile: The named cost profile ('fastest', 'shortest', 'balanced').
        
    Returns:
        A tuple of (total_cost, total_time).
    """
    if len(route) < 2:
        return 0.0, 0.0
        
    weights = PROFILES.get(profile, PROFILES["balanced"])
    alpha, beta, gamma = weights["alpha"], weights["beta"], weights["gamma"]
    
    current_time = depart_time
    total_cost = 0.0
    
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        
        # Edge handling
        if graph.is_multigraph():
            edge_data_dict = graph.get_edge_data(u, v)
            min_edge_key = min(edge_data_dict.keys(), key=lambda k: edge_data_dict[k].get('travel_time', float('inf')))
            edge_data = edge_data_dict[min_edge_key]
        else:
            edge_data = graph[u][v]
            
        tt = edge_travel_time(graph, u, v, current_time)
        dist = edge_data.get('length', 100.0)
        
        # Jerk/congestion penalty: difference between time-dependent TT and free-flow TT
        free_flow = edge_data.get('travel_time', dist / 10.0)
        jerk = max(0.0, tt - free_flow)
        
        # Composite edge cost
        c_e = alpha * tt + beta * dist + gamma * jerk
        total_cost += c_e
        
        # Arrival time updates the clock
        current_time += tt
        
    total_time = current_time - depart_time
    
    return total_cost, total_time
