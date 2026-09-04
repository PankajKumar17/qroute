import numpy as np

def traffic_multiplier(hour_of_day: float, edge_type: str = "default") -> float:
    """
    Returns a congestion multiplier based on a synthetic diurnal pattern.
    Assumes rush hours at 8-10am and 5-7pm.
    
    Args:
        hour_of_day: Float representing the hour (0 to 24).
        edge_type: The type of edge (optional for varying behaviors).
        
    Returns:
        A multiplier >= 1.0 (1.0 = free-flow).
    """
    # Normalize to 24-hour cycle
    h = hour_of_day % 24
    
    # Morning rush: peak at 8.5
    morning_peak = np.exp(-0.5 * ((h - 8.5) / 1.5) ** 2)
    # Evening rush: peak at 18.0 (6pm)
    evening_peak = np.exp(-0.5 * ((h - 18.0) / 1.5) ** 2)
    
    # Base multiplier is 1.0. Rush hour can add up to 2.0 extra delay.
    return 1.0 + 1.5 * morning_peak + 2.0 * evening_peak

def edge_travel_time(graph, u, v, arrival_time: float) -> float:
    """
    Computes the realized travel time for an edge given the arrival time at node u.
    
    Args:
        graph: NetworkX graph.
        u: Source node.
        v: Target node.
        arrival_time: Time (in seconds from midnight) when leaving node u.
        
    Returns:
        Travel time in seconds.
    """
    # Free-flow time in seconds
    try:
        # MultiDiGraph
        edge_data = graph[u][v][0]
    except KeyError:
        # DiGraph
        edge_data = graph[u][v]
        
    free_flow = edge_data['travel_time']
    
    hour_of_day = (arrival_time / 3600.0) % 24.0
    multiplier = traffic_multiplier(hour_of_day)
    
    return free_flow * multiplier

def verify_fifo_consistency(graph, u, v, samples=100):
    """
    Checks if the time-dependent edge preserves the FIFO (First-In-First-Out) property.
    If a vehicle leaves u earlier, it must arrive at v earlier.
    
    Args:
        graph: NetworkX graph.
        u: Source node.
        v: Target node.
        samples: Number of samples over a day to check.
    """
    # Departure times from 0 to 24 hours (in seconds)
    departures = np.linspace(0, 24 * 3600, samples)
    
    arrivals = []
    for d in departures:
        tt = edge_travel_time(graph, u, v, d)
        arrivals.append(d + tt)
        
    # Check if arrivals is monotonically non-decreasing
    for i in range(1, len(arrivals)):
        assert arrivals[i] >= arrivals[i-1], f"FIFO violated at departure {departures[i]}"
