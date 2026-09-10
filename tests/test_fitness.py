import pytest
import networkx as nx
from qroute.graph.fitness import time_dependent_route_cost

def test_time_dependent_route_cost():
    G = nx.DiGraph()
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    # 30 mins each
    G.add_edge(0, 1, travel_time=1800)
    G.add_edge(1, 2, travel_time=1800)
    
    route = [0, 1, 2]
    
    # 3 AM (10800 seconds) - off peak
    cost_off_peak, time_off_peak = time_dependent_route_cost(G, route, depart_time=10800)
    
    # 8.5 AM (30600 seconds) - morning peak
    cost_peak, time_peak = time_dependent_route_cost(G, route, depart_time=30600)
    
    assert cost_off_peak > 0
    assert cost_peak > 0
    
    # Assert peak is strictly slower than off-peak
    assert cost_peak > cost_off_peak
    assert time_peak > time_off_peak
