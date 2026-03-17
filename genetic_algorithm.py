# -*- coding: utf-8 -*-
import math
import random

def haversine_distance(p1, p2):
    """Calcula a distância real entre dois pontos em KM."""
    R = 6371.0  # Raio da Terra em km
    lat1, lon1 = math.radians(p1.lat), math.radians(p1.lon)
    lat2, lon2 = math.radians(p2.lat), math.radians(p2.lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_fitness(route):
    """
    Calcula o custo da rota. 
    Quanto MENOR o valor, MELHOR a rota.
    """
    total_km = 0
    penalty = 0
    
    for i in range(len(route)):
        # 1. Somatória da distância (Custo Geográfico)
        if i < len(route) - 1:
            total_km += haversine_distance(route[i], route[i+1])
        
        # 2. Lógica de Penalidade por Prioridade (Custo Clínico)
        # Se um ponto de prioridade 4 (Emergência) aparecer tarde na rota (i alto),
        # o fitness sobe drasticamente, forçando o algoritmo a movê-lo para o início.
        # i+1 representa a ordem (1º, 2º, 3º...). 
        # Multiplicamos a posição pelo peso da prioridade.
        peso_prioridade = route[i].prioridade # Valores de 1 a 4
        
        # Penalidade: Prioridade alta (4) em posição alta (ex: 15º) = Custo enorme.
        # Usamos (i * peso) para que o GA sinta "dor" ao atrasar emergências.
        penalty += (i * (peso_prioridade ** 2)) * 10 

    # O Fitness final é a distância física + as penalidades clínicas
    return total_km + penalty

def generate_random_population(points, size):
    population = []
    for _ in range(size):
        ind = points[:]
        random.shuffle(ind)
        population.append(ind)
    return population

def sort_population(population):
    # Retorna a população ordenada pelo fitness (do menor para o maior)
    fitness_values = [(ind, calculate_fitness(ind)) for ind in population]
    fitness_values.sort(key=lambda x: x[1])
    return [x[0] for x in fitness_values], [x[1] for x in fitness_values]

def evolve_population(population, pop_size, mutation_rate):
    # 1. Ordena e seleciona os melhores (Elitismo)
    population, fitness_values = sort_population(population)
    next_gen = population[:pop_size // 5] # Mantém 20% melhores
    
    # 2. Crossover e Mutação
    while len(next_gen) < pop_size:
        parent1 = random.choice(population[:pop_size // 2])
        parent2 = random.choice(population[:pop_size // 2])
        
        # Crossover simples (Ordered Crossover)
        child = crossover(parent1, parent2)
        
        # Mutação
        if random.random() < mutation_rate:
            mutate(child)
            
        next_gen.append(child)
        
    best_route = population[0]
    best_fit = fitness_values[0]
    return next_gen, best_route, best_fit

def crossover(p1, p2):
    size = len(p1)
    a, b = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[a:b] = p1[a:b]
    
    p2_remaining = [item for item in p2 if item not in child]
    idx = 0
    for i in range(size):
        if child[i] is None:
            child[i] = p2_remaining[idx]
            idx += 1
    return child

def mutate(route):
    # Troca dois pontos de lugar (Swap Mutation)
    a, b = random.sample(range(len(route)), 2)
    route[a], route[b] = route[b], route[a]