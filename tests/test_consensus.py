import pytest
from qroute.consensus.redundant_consensus import check_consensus, route_similarity

def test_consensus():
    # Construct identical and totally different routes
    route_a = [[1, 2], [3, 4]]
    route_b = [[1, 2], [3, 4]]
    route_c = [[4, 3], [2, 1]] # Divergent
    
    # 1. Consensus reached
    bests_reached = [route_a, route_b, route_b, route_c]
    consensus_sol = check_consensus(bests_reached, similarity_threshold=0.9, redundancy_threshold=2)
    assert consensus_sol is not None
    assert consensus_sol == route_a or consensus_sol == route_b
    
    # 2. Consensus NOT reached
    bests_not_reached = [route_a, route_c, [[1, 3], [2, 4]], [[1, 4], [2, 3]]]
    consensus_sol2 = check_consensus(bests_not_reached, similarity_threshold=0.9, redundancy_threshold=2)
    assert consensus_sol2 is None

def test_route_similarity():
    sim = route_similarity([[1, 2]], [[1, 2]])
    assert sim == 1.0
    
    sim2 = route_similarity([[1, 2]], [[2, 1]])
    # Edges A: (0, 1), (1, 2), (2, 0)
    # Edges B: (0, 2), (2, 1), (1, 0)
    # Directed edges! Overlap = 0
    assert sim2 == 0.0
