from qroute.graph.fitness import time_dependent_route_cost

def apply_two_opt(graph_route: list, graph, depart_time: float = 0.0) -> list:
    """
    Applies the 2-opt local search algorithm to untangle a given vehicle route.
    Assumes graph_route starts and ends at the depot (e.g., [0, 4, 2, 1, 0]).
    """
    best_route = graph_route[:]
    improved = True
    
    while improved:
        improved = False
        
        # Calculate current cost once per pass to save compute
        current_cost, _ = time_dependent_route_cost(graph, best_route, depart_time)
        
        # Iterate over all pairs of edges (excluding the depot ends from reversal)
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:
                    continue  # Reversing a single edge does nothing
                
                # Perform 2-opt swap (reverse the segment between i and j)
                new_route = best_route[:]
                new_route[i:j] = best_route[j-1:i-1:-1]
                
                new_cost, _ = time_dependent_route_cost(graph, new_route, depart_time)
                
                if new_cost < current_cost:
                    best_route = new_route
                    current_cost = new_cost
                    improved = True
                    break # Break out to restart the search with the new best route
            if improved:
                break
                
    return best_route
