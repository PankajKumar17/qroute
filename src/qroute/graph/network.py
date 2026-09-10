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
        
    # Generate a random geometric graph for positions
    G_undirected = nx.random_geometric_graph(n_nodes, radius=100.0, seed=seed)
    
    # Convert to complete directed graph for VRP routing
    G = nx.complete_graph(n_nodes, create_using=nx.DiGraph)
    
    # Add coordinates as node attributes (x, y) if they are in 'pos'
    for node in G.nodes():
        if node in G_undirected.nodes() and 'pos' in G_undirected.nodes[node]:
            pos = G_undirected.nodes[node]['pos']
            G.nodes[node]['pos'] = pos
            G.nodes[node]['x'] = pos[0]
            G.nodes[node]['y'] = pos[1]
    
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

def build_vrp_graph_from_road_network(G_road: nx.MultiDiGraph, n_customers: int, seed: int = None) -> nx.DiGraph:
    """
    Samples nodes from a real road network and computes all-pairs shortest paths 
    to build a complete directed graph for VRP optimization.
    
    Args:
        G_road: OSMnx road network graph.
        n_customers: Number of customers (total nodes will be n_customers + 1 for depot).
        seed: Random seed.
        
    Returns:
        A NetworkX DiGraph (complete) with 'length', 'travel_time', and 'path_nodes' attributes.
    """
    if seed is not None:
        np.random.seed(seed)
        
    # Sample nodes that belong to the largest strongly connected component
    # to ensure paths exist between all sampled nodes.
    scc = max(nx.strongly_connected_components(G_road), key=len)
    scc_nodes = list(scc)
    
    # We need n_customers + 1 nodes (depot is index 0)
    total_nodes = n_customers + 1
    sampled_nodes = np.random.choice(scc_nodes, size=total_nodes, replace=False)
    
    # Build complete graph where node IDs are 0 to n_customers
    G_vrp = nx.complete_graph(total_nodes, create_using=nx.DiGraph)
    
    # Add coordinate attributes from the original graph
    for idx, node_id in enumerate(sampled_nodes):
        G_vrp.nodes[idx]['osmnx_id'] = node_id
        G_vrp.nodes[idx]['x'] = G_road.nodes[node_id]['x']
        G_vrp.nodes[idx]['y'] = G_road.nodes[node_id]['y']
        
    # Compute all-pairs shortest paths on the road network (using travel_time)
    # Since G_road is a MultiDiGraph, shortest_path uses the edge with the lowest weight automatically
    for u in range(total_nodes):
        u_osm = sampled_nodes[u]
        
        # single_source_dijkstra computes paths and lengths to all reachable nodes
        lengths, paths = nx.single_source_dijkstra(G_road, u_osm, weight='travel_time')
        
        for v in range(total_nodes):
            if u == v:
                continue
                
            v_osm = sampled_nodes[v]
            
            # Extract distance and path
            travel_time = lengths[v_osm]
            path = paths[v_osm]
            
            # Compute physical length of this path
            length = 0.0
            for i in range(len(path) - 1):
                # get edge data (MultiDiGraph, take min travel_time edge)
                edge_data = G_road.get_edge_data(path[i], path[i+1])
                min_edge = min(edge_data.values(), key=lambda x: x.get('travel_time', float('inf')))
                length += min_edge.get('length', 0.0)
                
            G_vrp[u][v]['travel_time'] = travel_time
            G_vrp[u][v]['length'] = length
            G_vrp[u][v]['path_nodes'] = path
            
    return G_vrp
