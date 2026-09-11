from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np

from qroute.graph.network import build_synthetic_graph, load_road_network, build_vrp_graph_from_road_network
from qroute.algorithms.adaptive_pso import adaptive_pso
from qroute.consensus.redundant_consensus import darwinism_consensus
from qroute.robustness.scenario_testing import generate_traffic_scenarios, evaluate_route_robustness
from qroute.algorithms.local_search import apply_two_opt

app = FastAPI(title="Q-Route API")

# Enable CORS for the React frontend (when running in dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizeRequest(BaseModel):
    graph_type: str = "Piedmont" # Default to real roads now
    n_customers: int = 20
    vehicle_capacity: int = 50
    swarm_size: int = 20
    iterations: int = 50
    k_subswarms: int = 3

class RouteResponse(BaseModel):
    vehicle_id: int
    route: List[int]
    graph_route: List[int]
    path_coordinates: List[List[float]]
    metrics: Dict[str, Any]

class OptimizeResponse(BaseModel):
    status: str
    best_fitness: float
    history: List[float]
    routes: List[RouteResponse]
    nodes: List[Dict[str, Any]]

# Global cache for road network
G_road_cache = None

def get_road_network():
    global G_road_cache
    if G_road_cache is None:
        G_road_cache = load_road_network("Piedmont, California, USA")
    return G_road_cache

@app.post("/api/optimize", response_model=OptimizeResponse)
def run_optimization(req: OptimizeRequest):
    try:
        # Generate Graph
        if req.graph_type == "Synthetic":
            G = build_synthetic_graph(req.n_customers + 1, seed=42)
        else:
            G_road = get_road_network()
            G = build_vrp_graph_from_road_network(G_road, req.n_customers, seed=42)
            
        demands = list(np.random.randint(5, 20, size=req.n_customers))
        
        # Run Algorithm
        if req.k_subswarms > 1:
            best_fitness, best_routes, _, _ = darwinism_consensus(G, demands, req.vehicle_capacity, k_subswarms=req.k_subswarms, iterations_per_window=req.iterations)
            history = [best_fitness]
        else:
            best_fitness, best_routes, history, log = adaptive_pso(G, demands, req.vehicle_capacity, req.swarm_size, req.iterations)
            
        # Robustness Scenarios
        scenarios = generate_traffic_scenarios(G, 20)
        
        # Format Nodes for Map
        nodes = []
        for node, data in G.nodes(data=True):
            if req.graph_type == "Synthetic":
                lat = 40.7128 + (float(data['y']) - 0.5) * 0.1
                lng = -74.0060 + (float(data['x']) - 0.5) * 0.1
            else:
                lat = float(data['y'])
                lng = float(data['x'])
                
            nodes.append({
                "id": node,
                "is_depot": node == 0,
                "demand": 0 if node == 0 else int(demands[node-1]),
                "lat": lat,
                "lng": lng
            })
            
        route_responses = []
        for idx, route in enumerate(best_routes):
            graph_route = [0] + [c + 1 for c in route] + [0]
            
            # Apply 2-opt local search to untangle crossed lines
            graph_route = apply_two_opt(graph_route, G, 0.0)
            
            metrics = evaluate_route_robustness(G, graph_route, 0.0, scenarios)
            
            # Calculate path coordinates for detailed drawing on streets
            path_coords = []
            if req.graph_type != "Synthetic":
                for i in range(len(graph_route) - 1):
                    u = graph_route[i]
                    v = graph_route[i+1]
                    path_nodes = G[u][v]['path_nodes']
                    
                    for p in path_nodes[:-1]:
                        p_lat = G_road.nodes[p]['y']
                        p_lng = G_road.nodes[p]['x']
                        path_coords.append([p_lat, p_lng])
                
                # add the very last node
                last_node = G[graph_route[-2]][graph_route[-1]]['path_nodes'][-1]
                path_coords.append([G_road.nodes[last_node]['y'], G_road.nodes[last_node]['x']])
            else:
                # fallback for synthetic
                for n in graph_route:
                    nd = next((n_data for n_data in nodes if n_data['id'] == n), None)
                    if nd:
                        path_coords.append([nd['lat'], nd['lng']])
            
            # Strip depots for 'route' response attribute (which is just customer indices)
            clean_route = [c - 1 for c in graph_route[1:-1]]
            
            route_responses.append(RouteResponse(
                vehicle_id=idx + 1,
                route=clean_route,
                graph_route=graph_route,
                path_coordinates=path_coords,
                metrics=metrics
            ))
            
        return OptimizeResponse(
            status="success",
            best_fitness=best_fitness,
            history=history,
            routes=route_responses,
            nodes=nodes
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

import os
static_dir = os.environ.get("STATIC_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../frontend/dist"))
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
