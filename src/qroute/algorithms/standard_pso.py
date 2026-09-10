import numpy as np
from typing import List, Tuple
from qroute.encoding.random_key import encode_particle, decode_to_tour
from qroute.encoding.split import split_giant_tour
from qroute.graph.fitness import time_dependent_route_cost

class Particle:
    def __init__(self, n_customers: int, seed: int = None):
        self.position = encode_particle(n_customers, seed=seed)
        self.velocity = np.random.uniform(-0.1, 0.1, size=n_customers)
        self.pbest_position = np.copy(self.position)
        self.pbest_fitness = float('inf')
        self.current_fitness = float('inf')
        self.current_routes = []

def evaluate_particle(particle: Particle, graph, demands: List[float], vehicle_capacity: float, depart_time: float) -> float:
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

def standard_pso(graph, demands: List[float], vehicle_capacity: float, 
                 swarm_size: int = 30, iterations: int = 50, depart_time: float = 0.0) -> Tuple[float, List[List[int]], List[float]]:
    """
    Standard PSO using random-key encoding.
    
    Returns:
        Tuple of (best_fitness, best_routes, history_of_gbest)
    """
    n_customers = len(demands)
    swarm = [Particle(n_customers) for _ in range(swarm_size)]
    
    gbest_position = None
    gbest_fitness = float('inf')
    gbest_routes = []
    
    w = 0.7  # inertia
    c1 = 1.5 # cognitive
    c2 = 1.5 # social
    
    history = []
    
    for _ in range(iterations):
        for particle in swarm:
            fitness = evaluate_particle(particle, graph, demands, vehicle_capacity, depart_time)
            if fitness < gbest_fitness:
                gbest_fitness = fitness
                gbest_position = np.copy(particle.position)
                gbest_routes = particle.current_routes
                
        # Update velocities and positions
        for particle in swarm:
            r1 = np.random.uniform(0, 1, size=n_customers)
            r2 = np.random.uniform(0, 1, size=n_customers)
            
            cognitive = c1 * r1 * (particle.pbest_position - particle.position)
            social = c2 * r2 * (gbest_position - particle.position)
            
            particle.velocity = w * particle.velocity + cognitive + social
            particle.position = particle.position + particle.velocity
            
            # Keep positions in bounds (optional but good practice for random key)
            particle.position = np.clip(particle.position, 0.0, 1.0)
            
        history.append(gbest_fitness)
        
    return gbest_fitness, gbest_routes, history
