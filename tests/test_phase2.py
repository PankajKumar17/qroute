import pytest
import numpy as np
from qroute.encoding.random_key import encode_particle, decode_to_tour
from qroute.encoding.split import split_giant_tour
from qroute.algorithms.standard_pso import standard_pso
from qroute.graph.network import build_synthetic_graph

def test_phase2_verification(capsys):
    print("\n--- Phase 2 Verification ---")
    
    n_customers = 15
    np.random.seed(42)
    
    # (1) Decoded route from random particle
    particle = encode_particle(n_customers)
    tour = decode_to_tour(particle)
    is_valid = (len(tour) == n_customers) and (set(tour) == set(range(n_customers)))
    print(f"(1) Random Particle Tour: {tour}")
    print(f"    Valid Permutation (no missing/dup): {is_valid}")
    assert is_valid
    
    # (2) Split procedure capacity respect
    demands = [np.random.randint(10, 30) for _ in range(n_customers)]
    capacity = 50.0
    routes = split_giant_tour(tour, demands, capacity)
    print(f"(2) Split Routes (Capacity={capacity}):")
    capacity_respected = True
    for idx, r in enumerate(routes):
        load = sum(demands[c] for c in r)
        print(f"    Route {idx}: {r} (Load: {load})")
        if load > capacity:
            capacity_respected = False
    print(f"    Capacity Respected: {capacity_respected}")
    assert capacity_respected
    
    # (3) Short run of plain PSO
    G = build_synthetic_graph(n_nodes=n_customers + 1, seed=42)
    print("(3) PSO Convergence over 20 iterations:")
    # We will pass a callback to print best fitness per iteration, or just inspect history
    best_fitness, best_routes, history = standard_pso(
        graph=G, demands=demands, vehicle_capacity=capacity,
        swarm_size=20, iterations=20, depart_time=0.0
    )
    for i, fit in enumerate(history):
        print(f"    Iter {i}: Best Fitness = {fit:.2f}")
        
    assert history[-1] <= history[0], "Fitness should improve or stay the same"
    
    # (4) Shortest-path single-vehicle mode
    print("\n(4) Shortest-Path Single-Vehicle Mode (Infinite Capacity):")
    sp_fitness, sp_routes, sp_history = standard_pso(
        graph=G, demands=demands, vehicle_capacity=float('inf'),
        swarm_size=10, iterations=10, depart_time=0.0
    )
    print(f"    Resulting Routes: {sp_routes}")
    print(f"    Final Cost: {sp_fitness:.2f}")
    assert len(sp_routes) == 1, "Should result in exactly one route when capacity is infinite"

