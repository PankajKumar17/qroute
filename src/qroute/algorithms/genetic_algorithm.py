import numpy as np
import random
from typing import List, Tuple
from qroute.encoding.split import split_giant_tour
from qroute.graph.fitness import time_dependent_route_cost

def evaluate_tour(tour: List[int], graph, demands: List[float], vehicle_capacity: float, depart_time: float) -> Tuple[float, List[List[int]]]:
    routes = split_giant_tour(tour, demands, vehicle_capacity)
    total_cost = 0.0
    for r in routes:
        graph_route = [0] + [c + 1 for c in r] + [0]
        cost, _ = time_dependent_route_cost(graph, graph_route, depart_time)
        total_cost += cost
    return total_cost, routes

def order_crossover(parent1: List[int], parent2: List[int]) -> List[int]:
    n = len(parent1)
    start, end = sorted(random.sample(range(n), 2))
    
    child = [-1] * n
    child[start:end] = parent1[start:end]
    
    p2_idx = end
    c_idx = end
    
    while -1 in child:
        if parent2[p2_idx % n] not in child:
            child[c_idx % n] = parent2[p2_idx % n]
            c_idx += 1
        p2_idx += 1
        
    return child

def swap_mutation(tour: List[int], mutation_rate: float) -> List[int]:
    mutated = tour[:]
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(mutated) - 1)
            mutated[i], mutated[j] = mutated[j], mutated[i]
    return mutated

def genetic_algorithm(graph, demands: List[float], vehicle_capacity: float,
                      pop_size: int = 30, iterations: int = 50, depart_time: float = 0.0) -> Tuple[float, List[List[int]], List[float]]:
    """
    GA baseline for VRP using order crossover and swap mutation on permutations.
    """
    n_customers = len(demands)
    population = [list(np.random.permutation(n_customers)) for _ in range(pop_size)]
    
    gbest_fitness = float('inf')
    gbest_routes = []
    
    history = []
    
    for _ in range(iterations):
        fitnesses = []
        for ind in population:
            cost, routes = evaluate_tour(ind, graph, demands, vehicle_capacity, depart_time)
            fitnesses.append((cost, ind, routes))
            
            if cost < gbest_fitness:
                gbest_fitness = cost
                gbest_routes = routes
                
        # Sort by fitness
        fitnesses.sort(key=lambda x: x[0])
        history.append(gbest_fitness)
        
        # Elitism and selection
        new_population = [fitnesses[0][1], fitnesses[1][1]]
        
        while len(new_population) < pop_size:
            # Tournament selection
            p1 = min(random.sample(fitnesses, 3), key=lambda x: x[0])[1]
            p2 = min(random.sample(fitnesses, 3), key=lambda x: x[0])[1]
            
            child = order_crossover(p1, p2)
            child = swap_mutation(child, mutation_rate=0.1)
            
            new_population.append(child)
            
        population = new_population
        
    return gbest_fitness, gbest_routes, history
