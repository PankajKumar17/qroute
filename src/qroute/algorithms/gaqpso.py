"""
Gaussian distributed local attractor QPSO (GAQPSO).
Based on the Delta-Potential Well physics model but uses a Gaussian distribution
for the local attractor to improve diversity and prevent premature convergence.
"""
import numpy as np
from typing import List, Tuple
from qroute.encoding.random_key import encode_particle, decode_to_tour
from qroute.encoding.split import split_giant_tour
from qroute.graph.fitness import time_dependent_route_cost

class QPSOParticle:
    def __init__(self, n_customers: int, seed: int = None):
        self.position = encode_particle(n_customers, seed=seed)
        self.pbest_position = np.copy(self.position)
        self.pbest_fitness = float('inf')
        self.current_fitness = float('inf')
        self.current_routes = []

def evaluate_qpso_particle(particle: QPSOParticle, graph, demands: List[float], vehicle_capacity: float, depart_time: float) -> float:
    tour = decode_to_tour(particle.position)
    routes = split_giant_tour(tour, demands, vehicle_capacity)
    
    total_cost = 0.0
    for r in routes:
        graph_route = [0] + [c + 1 for c in r] + [0]
        cost, _ = time_dependent_route_cost(graph, graph_route, depart_time)
        total_cost += cost
        
    particle.current_fitness = total_cost
    particle.current_routes = routes
    
    if total_cost < particle.pbest_fitness:
        particle.pbest_fitness = total_cost
        particle.pbest_position = np.copy(particle.position)
        
    return total_cost

def calculate_diversity(positions: np.ndarray) -> float:
    """
    Calculate diversity metric:
    diversity = (1 / (L * M)) * sum_{i=1}^M || X_i - X_{mean} ||_2
    where L is the diagonal of the search space [0, 1]^D, L = sqrt(D)
    """
    M, D = positions.shape
    L = np.sqrt(D)
    mean_pos = np.mean(positions, axis=0)
    # Calculate Euclidean distance for each particle to the mean position
    distances = np.linalg.norm(positions - mean_pos, axis=1)
    return float(np.sum(distances) / (L * M))

def gaqpso(graph, demands: List[float], vehicle_capacity: float,
           swarm_size: int = 30, iterations: int = 50, depart_time: float = 0.0) -> Tuple[float, List[List[int]], List[float], List[float]]:
    n_customers = len(demands)
    swarm = [QPSOParticle(n_customers) for _ in range(swarm_size)]
    
    gbest_position = None
    gbest_fitness = float('inf')
    gbest_routes = []
    history = []
    diversity_history = []
    
    alpha_start = 1.0
    alpha_end = 0.5
    
    for iteration in range(iterations):
        alpha = alpha_start - (alpha_start - alpha_end) * (iteration / iterations)
        
        # Evaluate
        for particle in swarm:
            fitness = evaluate_qpso_particle(particle, graph, demands, vehicle_capacity, depart_time)
            if fitness < gbest_fitness:
                gbest_fitness = fitness
                gbest_position = np.copy(particle.position)
                gbest_routes = particle.current_routes
                
        history.append(gbest_fitness)
        
        # Calculate diversity of current positions
        positions = np.array([p.position for p in swarm])
        div = calculate_diversity(positions)
        diversity_history.append(div)
        
        # Mean best position
        mbest = np.mean([p.pbest_position for p in swarm], axis=0)
        
        # Update
        for particle in swarm:
            phi = np.random.uniform(0, 1, size=n_customers)
            # Original local attractor
            p = phi * particle.pbest_position + (1 - phi) * gbest_position
            
            # Standard deviation for Gaussian distribution
            sigma = np.abs(mbest - particle.pbest_position)
            
            # New local attractor np using Gaussian distribution
            # Note: np.random.normal takes loc (mean) and scale (std dev)
            np_attractor = np.random.normal(loc=p, scale=sigma)
            
            u = np.random.uniform(0, 1, size=n_customers)
            # Avoid log(0)
            u = np.maximum(u, 1e-10)
            
            L_val = alpha * np.abs(mbest - particle.position)
            
            sign = np.where(np.random.rand(n_customers) > 0.5, 1, -1)
            particle.position = np_attractor + sign * L_val * np.log(1.0 / u)
            particle.position = np.clip(particle.position, 0.0, 1.0)
            
    return gbest_fitness, gbest_routes, history, diversity_history
