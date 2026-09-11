"""
Canonical QPSO baseline using the Delta-Potential Well physics model (Sun et al. 2004).
This is purely a separate baseline algorithm, not used in the main Q-Route engine.
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

def canonical_qpso(graph, demands: List[float], vehicle_capacity: float,
                   swarm_size: int = 30, iterations: int = 50, depart_time: float = 0.0) -> Tuple[float, List[List[int]], List[float]]:
    n_customers = len(demands)
    swarm = [QPSOParticle(n_customers) for _ in range(swarm_size)]
    
    gbest_position = None
    gbest_fitness = float('inf')
    gbest_routes = []
    history = []
    
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
        
        # Mean best position
        mbest = np.mean([p.pbest_position for p in swarm], axis=0)
        
        # Update
        for particle in swarm:
            phi = np.random.uniform(0, 1, size=n_customers)
            p = phi * particle.pbest_position + (1 - phi) * gbest_position
            u = np.random.uniform(0, 1, size=n_customers)
            L = alpha * np.abs(mbest - particle.position)
            
            sign = np.where(np.random.rand(n_customers) > 0.5, 1, -1)
            particle.position = p + sign * L * np.log(1.0 / u)
            particle.position = np.clip(particle.position, 0.0, 1.0)
            
    return gbest_fitness, gbest_routes, history
