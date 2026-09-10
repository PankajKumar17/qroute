import numpy as np
from typing import List, Tuple
from qroute.algorithms.standard_pso import Particle, evaluate_particle
from qroute.algorithms.diversity import swarm_diversity
from qroute.algorithms.quantum_walk import quantum_walk_sample

def adaptive_pso(graph, demands: List[float], vehicle_capacity: float, 
                 swarm_size: int = 30, iterations: int = 50, depart_time: float = 0.0,
                 w_stagnation: int = 5, epsilon: float = 1e-4, d_min: float = 0.2,
                 reseed_fraction: float = 0.3, top_k_preserve: int = 2) -> Tuple[float, List[List[int]], List[float], List[dict]]:
    """
    Adaptive PSO with stagnation detection and quantum-walk reseeding.
    """
    n_customers = len(demands)
    swarm = [Particle(n_customers) for _ in range(swarm_size)]
    
    gbest_position = None
    gbest_fitness = float('inf')
    gbest_routes = []
    
    w = 0.7
    c1 = 1.5
    c2 = 1.5
    
    history = []
    reseed_log = []
    
    for iteration in range(iterations):
        for particle in swarm:
            fitness = evaluate_particle(particle, graph, demands, vehicle_capacity, depart_time)
            if fitness < gbest_fitness:
                gbest_fitness = fitness
                gbest_position = np.copy(particle.position)
                gbest_routes = particle.current_routes
                
        history.append(gbest_fitness)
        
        # Stagnation detection
        if iteration >= w_stagnation:
            improvement = history[-w_stagnation] - gbest_fitness
            div = swarm_diversity([p.position for p in swarm])
            
            if improvement < epsilon and div < d_min:
                # Trigger reseed
                # Sort swarm by pbest_fitness (ascending)
                swarm.sort(key=lambda p: p.pbest_fitness)
                
                # Replace worst fraction
                n_replace = int(swarm_size * reseed_fraction)
                # Ensure we don't replace top_k
                start_replace_idx = max(top_k_preserve, swarm_size - n_replace)
                
                new_samples = quantum_walk_sample(graph, swarm_size - start_replace_idx)
                
                for i in range(start_replace_idx, swarm_size):
                    swarm[i] = Particle(n_customers)
                    swarm[i].position = new_samples[i - start_replace_idx]
                    
                div_after = swarm_diversity([p.position for p in swarm])
                
                reseed_log.append({
                    'iteration': iteration,
                    'diversity_before': div,
                    'diversity_after': div_after,
                    'fitness_before': history[-w_stagnation],
                    'fitness_after': gbest_fitness
                })
                
        # Update velocities and positions
        for particle in swarm:
            r1 = np.random.uniform(0, 1, size=n_customers)
            r2 = np.random.uniform(0, 1, size=n_customers)
            
            cognitive = c1 * r1 * (particle.pbest_position - particle.position)
            social = c2 * r2 * (gbest_position - particle.position)
            
            particle.velocity = w * particle.velocity + cognitive + social
            particle.position = particle.position + particle.velocity
            particle.position = np.clip(particle.position, 0.0, 1.0)
            
    return gbest_fitness, gbest_routes, history, reseed_log
