import pytest
import numpy as np
from qroute.encoding.random_key import encode_particle, decode_to_tour

def test_decode_to_tour():
    for _ in range(100):
        n = np.random.randint(5, 50)
        keys = encode_particle(n)
        tour = decode_to_tour(keys)
        
        # Check length
        assert len(tour) == n
        # Check valid permutation
        assert set(tour) == set(range(n))
        # No duplicates
        assert len(set(tour)) == len(tour)
