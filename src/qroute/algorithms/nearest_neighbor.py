from typing import List
from qroute.graph.traffic import edge_travel_time

def nearest_neighbor_vrp(graph, demands: List[float], vehicle_capacity: float, depart_time: float = 0.0) -> List[List[int]]:
    """
    Nearest neighbor construction heuristic for the VRP.
    
    Args:
        graph: NetworkX graph (assumes complete graph for simplicity).
        demands: List of customer demands (index 0 is customer 0, but in graph they are nodes 1..N).
        vehicle_capacity: Maximum capacity per vehicle.
        depart_time: Time of departure from depot.
        
    Returns:
        List of sub-routes.
    """
    unvisited = set(range(1, len(demands) + 1))
    routes = []
    
    current_time = depart_time
    
    while unvisited:
        current_node = 0 # Start at depot
        current_route = []
        current_load = 0.0
        
        while unvisited:
            best_customer = None
            best_cost = float('inf')
            
            for customer in unvisited:
                demand = demands[customer - 1]
                if current_load + demand <= vehicle_capacity:
                    # Evaluate time to reach customer
                    tt = edge_travel_time(graph, current_node, customer, current_time)
                    if tt < best_cost:
                        best_cost = tt
                        best_customer = customer
                        
            if best_customer is None:
                # No customer can fit in the current vehicle
                break
                
            # Move to best customer
            current_route.append(best_customer - 1) # Store customer index (0-based)
            current_load += demands[best_customer - 1]
            unvisited.remove(best_customer)
            current_time += best_cost
            current_node = best_customer
            
        if not current_route:
            # Should not happen unless a single customer exceeds capacity
            c = list(unvisited)[0]
            if demands[c - 1] > vehicle_capacity:
                raise ValueError(f"Customer {c-1} demand exceeds vehicle capacity.")
                
        routes.append(current_route)
        
        # Return to depot time
        current_time += edge_travel_time(graph, current_node, 0, current_time)
        
    return routes
