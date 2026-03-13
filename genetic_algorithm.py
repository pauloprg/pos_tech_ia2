# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 23:56:09 2026

@author: paulo
"""

import random
import math
from typing import List
from pontos import ServicePoint


CAPACIDADE = 25
HORARIO_INICIO = 8
FATOR_TEMPO = 0.03
PENALIDADE_TEMPERATURA = 180
ESPERA_PROT_ESPECIAL = 1.5


def euclidean_distance(p1: ServicePoint, p2: ServicePoint) -> float:
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def route_distance(route: List[ServicePoint]) -> float:
    if len(route) < 2:
        return 0.0

    total = 0.0
    for i in range(len(route) - 1):
        total += euclidean_distance(route[i], route[i + 1])
    return total


def priority_penalty(point: ServicePoint, current_time: float) -> float:
    if current_time <= point.tempo_fim:
        return 0.0

    delay = current_time - point.tempo_fim

    if point.prioridade == 4:
        base_penalty = delay * 300
    elif point.prioridade == 3:
        base_penalty = delay * 180
    elif point.prioridade == 2:
        base_penalty = delay * 100
    else:
        base_penalty = delay * 60

    if point.protocolo_especial:
        base_penalty *= ESPERA_PROT_ESPECIAL

    return base_penalty


def time_window_penalty(point: ServicePoint, current_time: float) -> float:
    """
    Penaliza atendimento fora da janela de tempo.
    Se chegar antes, pode esperar.
    Se chegar depois, penaliza.
    """
    if current_time < point.tempo_inicio:
        return 0.0

    if current_time > point.tempo_fim:
        return (current_time - point.tempo_fim) * 120

    return 0.0


def capacity_penalty(route: List[ServicePoint]) -> float:
    total_demand = sum(point.quantidade for point in route)

    if total_demand <= CAPACIDADE:
        return 0.0

    excess = total_demand - CAPACIDADE
    return excess * 250


def refrigeration_penalty(point: ServicePoint, travel_segment_time: float) -> float:
    if not point.temperatura_controlada:
        return 0.0

    if travel_segment_time <= 2.5:
        return 0.0

    return (travel_segment_time - 2.5) * PENALIDADE_TEMPERATURA


def calculate_fitness(route: List[ServicePoint]) -> float:
    """
    Quanto menor o fitness, melhor a rota.
    Fitness = distância + penalidades.
    """
    if not route:
        return float("inf")

    total_cost = 0.0
    current_time = HORARIO_INICIO

    for i in range(len(route)):
        point = route[i]

        if i > 0:
            dist = euclidean_distance(route[i - 1], point)
            travel_time = dist * FATOR_TEMPO
            total_cost += dist
            total_cost += refrigeration_penalty(point, travel_time)
            current_time += travel_time

        if current_time < point.tempo_inicio:
            current_time = point.tempo_inicio

        total_cost += time_window_penalty(point, current_time)
        total_cost += priority_penalty(point, current_time)

        current_time += point.tempo_atendimento

    total_cost += capacity_penalty(route)

    return total_cost


def generate_random_population(points: List[ServicePoint], population_size: int) -> List[List[ServicePoint]]:
    population = []

    for _ in range(population_size):
        individual = points[:]
        random.shuffle(individual)
        population.append(individual)

    return population


def sort_population(population: List[List[ServicePoint]]) -> tuple[List[List[ServicePoint]], List[float]]:
    fitness_values = [calculate_fitness(individual) for individual in population]

    combined = list(zip(population, fitness_values))
    combined.sort(key=lambda item: item[1])

    sorted_population = [item[0] for item in combined]
    sorted_fitness = [item[1] for item in combined]

    return sorted_population, sorted_fitness


def selection_by_tournament(population: List[List[ServicePoint]], tournament_size: int = 4) -> List[ServicePoint]:
    competitors = random.sample(population, tournament_size)
    competitors.sort(key=calculate_fitness)
    return competitors[0][:]


def order_crossover(parent1: List[ServicePoint], parent2: List[ServicePoint]) -> List[ServicePoint]:
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))

    child = [None] * size
    child[start:end + 1] = parent1[start:end + 1]

    parent2_filtered = [point for point in parent2 if point not in child]

    idx = 0
    for i in range(size):
        if child[i] is None:
            child[i] = parent2_filtered[idx]
            idx += 1

    return child


def mutate(route: List[ServicePoint], mutation_probability: float) -> List[ServicePoint]:
    mutated = route[:]

    if random.random() < mutation_probability:
        i, j = sorted(random.sample(range(len(mutated)), 2))
        mutated[i], mutated[j] = mutated[j], mutated[i]

    if random.random() < mutation_probability * 0.5:
        i, j = sorted(random.sample(range(len(mutated)), 2))
        mutated[i:j + 1] = reversed(mutated[i:j + 1])

    return mutated


def evolve_population(
    population: List[List[ServicePoint]],
    population_size: int,
    mutation_probability: float,
    elite_size: int = 1
) -> tuple[List[List[ServicePoint]], List[ServicePoint], float]:
    population, fitness_values = sort_population(population)

    new_population = [individual[:] for individual in population[:elite_size]]

    while len(new_population) < population_size:
        parent1 = selection_by_tournament(population)
        parent2 = selection_by_tournament(population)

        child = order_crossover(parent1, parent2)
        child = mutate(child, mutation_probability)

        new_population.append(child)

    best_individual = population[0][:]
    best_fitness = fitness_values[0]

    return new_population, best_individual, best_fitness