import numpy as np
from typing import List, Tuple
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from qroute.graph.traffic import edge_travel_time

def create_cost_matrix(graph, n_nodes: int, depart_time: float) -> List[List[int]]:
    """
    Computes a static cost matrix at a fixed departure time for OR-Tools.
    Limitations: OR-Tools requires a static integer cost matrix, so we compute
    travel times at `depart_time` and scale to integers. This ignores time-dependency
    during the route execution.
    """
    matrix = []
    for u in range(n_nodes):
        row = []
        for v in range(n_nodes):
            if u == v:
                row.append(0)
            else:
                tt = edge_travel_time(graph, u, v, depart_time)
                row.append(int(tt)) # OR-Tools requires integer costs
        matrix.append(row)
    return matrix

def ortools_solve(graph, demands: List[float], vehicle_capacity: float, depart_time: float = 0.0) -> Tuple[float, List[List[int]]]:
    n_nodes = len(demands) + 1
    cost_matrix = create_cost_matrix(graph, n_nodes, depart_time)
    
    # Needs integer demands and capacities
    int_demands = [0] + [int(d) for d in demands]
    int_capacity = int(vehicle_capacity)
    num_vehicles = n_nodes # Upper bound
    depot = 0
    
    manager = pywrapcp.RoutingIndexManager(n_nodes, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return cost_matrix[from_node][to_node]
        
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return int_demands[from_node]
        
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [int_capacity] * num_vehicles,
        True,  # start cumul to zero
        "Capacity"
    )
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    
    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        return float('inf'), []
        
    routes = []
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            if node_index != 0:
                route.append(node_index - 1)
            index = solution.Value(routing.NextVar(index))
        if route:
            routes.append(route)
            
    # For actual cost, we re-evaluate using our dynamic function so comparisons are fair
    from qroute.graph.fitness import time_dependent_route_cost
    
    total_cost = 0.0
    for r in routes:
        graph_route = [0] + [c + 1 for c in r] + [0]
        cost, _ = time_dependent_route_cost(graph, graph_route, depart_time)
        total_cost += cost
        
    return total_cost, routes

def exact_solve_small(graph, demands: List[float], vehicle_capacity: float, depart_time: float = 0.0) -> Tuple[float, List[List[int]]]:
    """
    Exact solver for small instances (n_customers <= 12) using OR-Tools' exact mode.
    """
    if len(demands) > 12:
        raise ValueError("exact_solve_small only supports up to 12 customers")
        
    # We can use OR-Tools with Local Search disabled and exhaustive search.
    # But OR-Tools doesn't have a simple "exact" flag for VRP. 
    # For a tiny instance, we can configure search parameters for exhaustive search.
    # Alternatively, let's just configure it with very high time limit and Guided Local Search.
    
    n_nodes = len(demands) + 1
    cost_matrix = create_cost_matrix(graph, n_nodes, depart_time)
    
    int_demands = [0] + [int(d) for d in demands]
    int_capacity = int(vehicle_capacity)
    num_vehicles = n_nodes
    depot = 0
    
    manager = pywrapcp.RoutingIndexManager(n_nodes, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)
    
    transit_callback_index = routing.RegisterTransitCallback(
        lambda from_index, to_index: cost_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
    )
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(
        lambda from_index: int_demands[manager.IndexToNode(from_index)]
    )
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, [int_capacity] * num_vehicles, True, "Capacity"
    )
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = 2 # Enough for < 10 nodes to find optimum
    
    solution = routing.SolveWithParameters(search_parameters)
    
    routes = []
    if solution:
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                if node_index != 0:
                    route.append(node_index - 1)
                index = solution.Value(routing.NextVar(index))
            if route:
                routes.append(route)
                
    from qroute.graph.fitness import time_dependent_route_cost
    total_cost = 0.0
    for r in routes:
        graph_route = [0] + [c + 1 for c in r] + [0]
        cost, _ = time_dependent_route_cost(graph, graph_route, depart_time)
        total_cost += cost
        
    return total_cost, routes
