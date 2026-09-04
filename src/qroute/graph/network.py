import networkx as nx
import osmnx as ox
import numpy as np

def load_road_network(place_name: str, network_type: str = "drive") -> nx.MultiDiGraph:
    """
    Loads a road network for a given place using OSMnx, and adds travel times.
    
    Args:
        place_name: Location string (e.g., "Piedmont, California, USA").
        network_type: Type of street network. Default is "drive".
        
    Returns:
        A NetworkX MultiDiGraph with 'length' (meters) and 'travel_time' (seconds) on edges.
    """
    # Fetch graph from OSMnx
    G = ox.graph_from_place(place_name, network_type=network_type)
    
    # Impute missing edge speeds and calculate travel times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    
    # Ensure all edges have 'travel_time' and 'length'
    for u, v, key, data in G.edges(keys=True, data=True):
        if 'travel_time' not in data:
            # Fallback if ox.add_edge_travel_times missed it (rare, but just in case)
            length = data.get('length', 100.0)
            speed = data.get('speed_kph', 36.0) # 10 m/s default
            data['travel_time'] = length / (speed * 1000 / 3600)
            
    return G

def build_synthetic_graph(n_nodes: int, seed: int = None) -> nx.DiGraph:
    """
    Builds a random geometric graph as a fallback.
    
    Args:
        n_nodes: Number of nodes.
        seed: Random seed.
        
    Returns:
        A NetworkX DiGraph with 'length' and 'travel_time' attributes.
    """
    if seed is not None:
        np.random.seed(seed)
        
    # Generate a random geometric graph
    radius = 1.5 * np.sqrt(np.log(n_nodes) / n_nodes) if n_nodes > 0 else 0.5
    G_undirected = nx.random_geometric_graph(n_nodes, radius, seed=seed)
    
    # Convert to directed graph for routing
    G = nx.DiGraph(G_undirected)
    
    # Add coordinates as node attributes (x, y) if they are in 'pos'
    for node, data in G.nodes(data=True):
        if 'pos' in data:
            data['x'] = data['pos'][0]
            data['y'] = data['pos'][1]
    
    # Assign edge attributes
    for u, v, data in G.edges(data=True):
        pos_u = G.nodes[u]['pos']
        pos_v = G.nodes[v]['pos']
        # Distance in abstract units, scale to pretend meters
        dist = np.linalg.norm(np.array(pos_u) - np.array(pos_v)) * 10000 
        data['length'] = dist
        
        # Free-flow speed: say 10 to 20 m/s
        speed = np.random.uniform(10, 20)
        data['travel_time'] = dist / speed
        
    return G
