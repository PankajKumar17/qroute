import pytest
import networkx as nx
from qroute.graph.network import build_synthetic_graph

def test_build_synthetic_graph():
    n_nodes = 50
    G = build_synthetic_graph(n_nodes, seed=42)
    
    assert isinstance(G, nx.DiGraph)
    assert G.number_of_nodes() == n_nodes
    assert G.number_of_edges() > 0
    
    for u, v, data in G.edges(data=True):
        assert 'length' in data
        assert 'travel_time' in data
        assert data['length'] >= 0
        assert data['travel_time'] > 0
