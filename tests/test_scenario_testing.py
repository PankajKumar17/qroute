import pytest
import networkx as nx
from qroute.robustness.scenario_testing import evaluate_route_robustness

def test_scenario_testing_cv_ranking():
    G = nx.DiGraph()
    # Route 1: 0 -> 1 -> 2
    # Route 2: 0 -> 3 -> 4
    for i in range(5):
        G.add_node(i)
        
    G.add_edge(0, 1, travel_time=100)
    G.add_edge(1, 2, travel_time=100)
    
    G.add_edge(0, 3, travel_time=120)
    G.add_edge(3, 4, travel_time=120)
    
    route_a = [0, 1, 2] # Mean 200, highly volatile
    route_b = [0, 3, 4] # Mean 240, very stable
    
    # Construct scenarios manually to simulate the volatility
    scenarios = [
        {(0, 1): 1.0, (1, 2): 1.0, (0, 3): 1.0, (3, 4): 1.0}, # Normal
        {(0, 1): 3.0, (1, 2): 3.0, (0, 3): 1.1, (3, 4): 1.1}, # Route A gets huge shock
    ]
    
    res_a = evaluate_route_robustness(G, route_a, 0, scenarios)
    res_b = evaluate_route_robustness(G, route_b, 0, scenarios)
    
    # Route A should have lower mean (200 * 1 + 200 * 3)/2 = 400
    # Route B should have mean (240 * 1 + 240 * 1.1)/2 = 252
    # Wait, B actually has a lower mean in this contrived scenario. Let's adjust so A has lower mean.
    
    scenarios2 = [
        {(0, 1): 0.5, (1, 2): 0.5, (0, 3): 1.0, (3, 4): 1.0},
        {(0, 1): 2.0, (1, 2): 2.0, (0, 3): 1.0, (3, 4): 1.0},
    ]
    # A mean = 200 * (0.5+2.0)/2 = 250
    # B mean = 240 * 1 = 240. Still B is better.
    
    # Make A mean lower but high variance
    # A base = 100. Shocks: 1.0 and 2.0 -> mean 150.
    # B base = 160. Shocks: 1.0 and 1.0 -> mean 160.
    G[0][1]['travel_time'] = 50
    G[1][2]['travel_time'] = 50
    G[0][3]['travel_time'] = 80
    G[3][4]['travel_time'] = 80
    
    scenarios3 = [
        {(0, 1): 1.0, (1, 2): 1.0, (0, 3): 1.0, (3, 4): 1.0}, # A: 100, B: 160
        {(0, 1): 3.0, (1, 2): 3.0, (0, 3): 1.0, (3, 4): 1.0}, # A: 300, B: 160
    ]
    # A mean = 200, std = 100, CV = 0.5
    # B mean = 160, std = 0, CV = 0
    # We want A to have LOWER mean but HIGHER CV.
    
    scenarios4 = [
        {(0, 1): 0.5, (1, 2): 0.5, (0, 3): 0.95, (3, 4): 0.95}, # A: 50, B: 152
        {(0, 1): 2.1, (1, 2): 2.1, (0, 3): 1.05, (3, 4): 1.05}, # A: 210, B: 168
    ]
    # A mean = 130, std = 80 -> CV = 80/130 = 0.61
    # B mean = 160, std = 8 -> CV = 8/160 = 0.05
    
    res_a = evaluate_route_robustness(G, route_a, 0, scenarios4)
    res_b = evaluate_route_robustness(G, route_b, 0, scenarios4)
    
    assert res_a['mean'] < res_b['mean']
    assert res_a['cv'] > res_b['cv']
