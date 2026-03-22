# vrp_genetic.py
# -*- coding: utf-8 -*-

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from pontos import Depot, ServicePoint, Vehicle


@dataclass
class RoutePlan:
    vehicle: Vehicle
    points: List[ServicePoint]
    total_distance_km: float
    total_cost: float
    total_load: int
    total_stops: int
    infeasible_reasons: List[str]


@dataclass
class VRPSolution:
    chromosome: List[ServicePoint]
    routes: List[RoutePlan]
    fitness: float


# -----------------------------
# Distância / tempo
# -----------------------------
def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def distance_between(a, b) -> float:
    return haversine_distance(a.lat, a.lon, b.lat, b.lon)


# -----------------------------
# Penalidades
# -----------------------------
PENALTY_UNASSIGNED = 20000
PENALTY_INCOMPATIBLE = 15000
PENALTY_OVER_DISTANCE = 300
PENALTY_OVER_STOPS = 2000
PENALTY_OVER_LOAD = 4000
PENALTY_LATE_WINDOW = 1000
PENALTY_PRIORITY_DELAY = 500
PENALTY_SPECIAL_PROTOCOL = 5000
PENALTY_COLD_CHAIN = 8000


def priority_weight(prioridade: int) -> int:
    # 4 = emergência obstétrica; 3 = violência doméstica; 2 = hormônios; 1 = pós-parto
    mapping = {
        4: 12,
        3: 8,
        2: 5,
        1: 3,
    }
    return mapping.get(prioridade, 1)


# -----------------------------
# Decodificação da solução
# -----------------------------
def build_routes(
    chromosome: List[ServicePoint],
    vehicles: List[Vehicle],
    depot: Depot,
) -> Tuple[List[RoutePlan], List[ServicePoint], float]:
    """
    Constrói rotas distribuindo os pontos ao longo da frota.
    Estratégia: greedy por melhor custo marginal respeitando compatibilidade.
    """
    routes_state = []
    for vehicle in vehicles:
        routes_state.append(
            {
                "vehicle": vehicle,
                "points": [],
                "distance": 0.0,
                "cost": 0.0,
                "load": 0,
                "stops": 0,
                "clock_hour": 8.0,   # início operacional
                "last_node": depot,
                "reasons": [],
            }
        )

    unassigned = []
    global_penalty = 0.0

    # Ordena implicitamente o cromossomo por prioridade alta primeiro
    ordered = sorted(
        chromosome,
        key=lambda p: (-p.prioridade, p.tempo_fim, -p.quantidade)
    )

    for point in ordered:
        best_route_idx = None
        best_incremental_score = float("inf")
        best_candidate_state = None

        for idx, rs in enumerate(routes_state):
            vehicle = rs["vehicle"]

            if not vehicle.pode_atender(point):
                continue

            leg_km = distance_between(rs["last_node"], point)
            return_km_if_close = distance_between(point, depot)

            new_distance = rs["distance"] + leg_km + return_km_if_close
            new_stops = rs["stops"] + 1
            new_load = rs["load"] + point.quantidade

            travel_hours = leg_km / max(vehicle.velocidade_kmh, 1)
            arrival_hour = rs["clock_hour"] + travel_hours

            lateness = max(0.0, arrival_hour - point.tempo_fim)
            priority_delay = max(0.0, arrival_hour - point.tempo_inicio) * priority_weight(point.prioridade)

            overload_penalty = 0.0
            if new_load > vehicle.capacidade_suprimentos:
                overload_penalty += (new_load - vehicle.capacidade_suprimentos) * PENALTY_OVER_LOAD

            overstop_penalty = 0.0
            if new_stops > vehicle.max_paradas:
                overstop_penalty += (new_stops - vehicle.max_paradas) * PENALTY_OVER_STOPS

            overdistance_penalty = 0.0
            if new_distance > vehicle.max_distancia_km:
                overdistance_penalty += (new_distance - vehicle.max_distancia_km) * PENALTY_OVER_DISTANCE

            late_penalty = lateness * PENALTY_LATE_WINDOW * priority_weight(point.prioridade)
            priority_penalty = priority_delay * PENALTY_PRIORITY_DELAY

            incremental_cost = leg_km * vehicle.custo_km

            score = (
                incremental_cost
                + overload_penalty
                + overstop_penalty
                + overdistance_penalty
                + late_penalty
                + priority_penalty
            )

            if score < best_incremental_score:
                best_incremental_score = score
                best_route_idx = idx
                best_candidate_state = {
                    "leg_km": leg_km,
                    "arrival_hour": arrival_hour,
                    "new_distance": new_distance,
                    "new_stops": new_stops,
                    "new_load": new_load,
                    "incremental_cost": incremental_cost,
                    "lateness": lateness,
                }

        if best_route_idx is None:
            unassigned.append(point)
            global_penalty += PENALTY_UNASSIGNED * priority_weight(point.prioridade)
            continue

        rs = routes_state[best_route_idx]
        rs["points"].append(point)
        rs["distance"] += best_candidate_state["leg_km"]
        rs["cost"] += best_candidate_state["incremental_cost"]
        rs["load"] = best_candidate_state["new_load"]
        rs["stops"] = best_candidate_state["new_stops"]

        # Espera pela janela, se chegou cedo
        start_service = max(best_candidate_state["arrival_hour"], point.tempo_inicio)
        rs["clock_hour"] = start_service + point.tempo_atendimento
        rs["last_node"] = point

    routes = []
    for rs in routes_state:
        vehicle = rs["vehicle"]

        if rs["points"]:
            back_km = distance_between(rs["last_node"], depot)
            rs["distance"] += back_km
            rs["cost"] += back_km * vehicle.custo_km

        reasons = []
        if rs["load"] > vehicle.capacidade_suprimentos:
            reasons.append("capacidade_suprimentos_excedida")
        if rs["stops"] > vehicle.max_paradas:
            reasons.append("max_paradas_excedido")
        if rs["distance"] > vehicle.max_distancia_km:
            reasons.append("max_distancia_excedida")

        routes.append(
            RoutePlan(
                vehicle=vehicle,
                points=rs["points"],
                total_distance_km=rs["distance"],
                total_cost=rs["cost"],
                total_load=rs["load"],
                total_stops=rs["stops"],
                infeasible_reasons=reasons,
            )
        )

    return routes, unassigned, global_penalty


def calculate_solution_fitness(
    chromosome: List[ServicePoint],
    vehicles: List[Vehicle],
    depot: Depot,
) -> Tuple[float, List[RoutePlan]]:
    routes, unassigned, penalty = build_routes(chromosome, vehicles, depot)

    total_distance = sum(r.total_distance_km for r in routes)
    total_cost = sum(r.total_cost for r in routes)

    # Penalidade extra por rotas inviáveis
    infeasibility_penalty = 0.0
    for route in routes:
        infeasibility_penalty += len(route.infeasible_reasons) * 10000

        for point_idx, point in enumerate(route.points):
            # prioridade alta muito tarde na rota = penalidade forte
            infeasibility_penalty += point_idx * priority_weight(point.prioridade) * 100

            if point.temperatura_controlada and not route.vehicle.suporta_temperatura_controlada:
                infeasibility_penalty += PENALTY_COLD_CHAIN

            if point.protocolo_especial and not route.vehicle.suporta_protocolo_especial:
                infeasibility_penalty += PENALTY_SPECIAL_PROTOCOL

    # Menor é melhor
    fitness = total_cost + total_distance + penalty + infeasibility_penalty
    if unassigned:
        fitness += len(unassigned) * 5000

    return fitness, routes


# -----------------------------
# Operadores genéticos
# -----------------------------
def generate_random_population(points: List[ServicePoint], size: int) -> List[List[ServicePoint]]:
    population = []
    for _ in range(size):
        individual = points[:]
        random.shuffle(individual)
        population.append(individual)
    return population


def crossover(parent1: List[ServicePoint], parent2: List[ServicePoint]) -> List[ServicePoint]:
    size = len(parent1)
    a, b = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[a:b] = parent1[a:b]

    p2_remaining = [item for item in parent2 if item not in child]
    idx = 0
    for i in range(size):
        if child[i] is None:
            child[i] = p2_remaining[idx]
            idx += 1
    return child


def mutate(individual: List[ServicePoint], mutation_rate: float = 0.2) -> None:
    if random.random() > mutation_rate or len(individual) < 2:
        return

    a, b = sorted(random.sample(range(len(individual)), 2))
    mutation_type = random.choice(["swap", "reverse", "insert"])

    if mutation_type == "swap":
        individual[a], individual[b] = individual[b], individual[a]

    elif mutation_type == "reverse":
        individual[a:b] = reversed(individual[a:b])

    else:  # insert
        point = individual.pop(b)
        individual.insert(a, point)


def tournament_selection(
    population: List[List[ServicePoint]],
    vehicles: List[Vehicle],
    depot: Depot,
    k: int = 4,
) -> List[ServicePoint]:
    candidates = random.sample(population, min(k, len(population)))
    scored = []
    for c in candidates:
        fitness, _ = calculate_solution_fitness(c, vehicles, depot)
        scored.append((fitness, c))
    scored.sort(key=lambda x: x[0])
    return scored[0][1]


def evolve_population(
    population: List[List[ServicePoint]],
    vehicles: List[Vehicle],
    depot: Depot,
    pop_size: int,
    mutation_rate: float,
    elite_ratio: float = 0.2,
) -> Tuple[List[List[ServicePoint]], VRPSolution]:
    scored_population = []
    for individual in population:
        fitness, routes = calculate_solution_fitness(individual, vehicles, depot)
        scored_population.append((fitness, individual, routes))

    scored_population.sort(key=lambda x: x[0])

    elite_count = max(2, int(pop_size * elite_ratio))
    next_gen = [item[1][:] for item in scored_population[:elite_count]]

    while len(next_gen) < pop_size:
        parent1 = tournament_selection(population, vehicles, depot)
        parent2 = tournament_selection(population, vehicles, depot)

        child = crossover(parent1, parent2)
        mutate(child, mutation_rate)
        next_gen.append(child)

    best_fitness, best_chromosome, best_routes = scored_population[0]
    best_solution = VRPSolution(
        chromosome=best_chromosome[:],
        routes=best_routes,
        fitness=best_fitness,
    )

    return next_gen, best_solution