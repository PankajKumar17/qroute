from typing import List

def split_giant_tour(tour: List[int], demands: List[float], vehicle_capacity: float) -> List[List[int]]:
    """
    Partitions a giant tour into feasible sub-routes respecting vehicle capacity.
    
    Implementation Note: This uses a greedy approximation instead of the exact
    shortest-path auxiliary graph approach (Prins 2004) for simplicity and speed.
    It iterates through the giant tour sequentially and assigns customers to the 
    current vehicle until capacity is met, at which point a new vehicle is started.
    
    Args:
        tour: List of customer indices.
        demands: List of customer demands corresponding to indices.
                 Note: demands index must match the values in the tour!
                 If tour=[0, 1], demands[0] is demand for customer 0.
        vehicle_capacity: Maximum capacity per vehicle.
        
    Returns:
        List of sub-routes (each sub-route is a list of customer indices).
    """
    routes = []
    current_route = []
    current_load = 0.0
    
    for customer in tour:
        demand = demands[customer]
        
        if demand > vehicle_capacity:
            raise ValueError(f"Customer {customer} demand ({demand}) exceeds vehicle capacity ({vehicle_capacity}).")
            
        if current_load + demand <= vehicle_capacity:
            current_route.append(customer)
            current_load += demand
        else:
            routes.append(current_route)
            current_route = [customer]
            current_load = demand
            
    if current_route:
        routes.append(current_route)
        
    return routes
