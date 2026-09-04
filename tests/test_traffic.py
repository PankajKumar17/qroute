import pytest
import networkx as nx
from qroute.graph.traffic import verify_fifo_consistency, traffic_multiplier

def test_fifo_consistency():
    G = nx.DiGraph()
    G.add_node(0)
    G.add_node(1)
    # Travel time is 600s = 10 mins
    G.add_edge(0, 1, travel_time=600)
    
    # Should not raise an assertion error
    verify_fifo_consistency(G, 0, 1, samples=100)
    verify_fifo_consistency(G, 0, 1, samples=1000)

def test_traffic_multiplier():
    # Base should be close to 1 at 3am
    assert traffic_multiplier(3.0) < 1.1
    # Should peak around 8.5am
    assert traffic_multiplier(8.5) > 1.5
    # Should peak around 18.0 (6pm)
    assert traffic_multiplier(18.0) > 1.5
