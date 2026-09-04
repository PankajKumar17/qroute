from typing import List, Tuple
from qroute.graph.traffic import edge_travel_time

def time_dependent_route_cost(graph, route: List[int], depart_time: float) -> Tuple[float, float]:
    """
    Computes the total travel time for a sequential route, updating the current
    clock time at each node to fetch the time-dependent edge cost.
    
    Args:
        graph: NetworkX graph.
        route: A list of node IDs to visit in order.
        depart_time: Time (in seconds from midnight) when departing the first node.
        
    Returns:
        A tuple of (total_cost, total_time). In this simple model, cost = time.
    """
    if len(route) < 2:
        return 0.0, 0.0
        
    current_time = depart_time
    
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        
        # Determine the time to traverse (u, v) at current_time
        tt = edge_travel_time(graph, u, v, current_time)
        current_time += tt
        
    total_time = current_time - depart_time
    total_cost = total_time
    
    return total_cost, total_time
