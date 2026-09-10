import pytest
from qroute.encoding.split import split_giant_tour

def test_split_giant_tour_valid():
    tour = [0, 1, 2, 3, 4]
    demands = [10, 20, 15, 30, 5]
    capacity = 40
    
    routes = split_giant_tour(tour, demands, capacity)
    
    # Expected greedy split:
    # Route 1: 0 (10), 1 (20) -> 30. Next is 15 -> exceeds 40.
    # Route 2: 2 (15). Next is 30 -> exceeds 40.
    # Route 3: 3 (30), 4 (5) -> 35.
    
    assert len(routes) == 3
    assert routes[0] == [0, 1]
    assert routes[1] == [2]
    assert routes[2] == [3, 4]
    
    # Check all customers appear exactly once
    flattened = [c for r in routes for c in r]
    assert set(flattened) == set(tour)
    assert len(flattened) == len(tour)
    
    # Check capacity constraints
    for r in routes:
        assert sum(demands[c] for c in r) <= capacity

def test_split_giant_tour_exceeds_capacity():
    tour = [0]
    demands = [50]
    capacity = 40
    
    with pytest.raises(ValueError, match="exceeds vehicle capacity"):
        split_giant_tour(tour, demands, capacity)
