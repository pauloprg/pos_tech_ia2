# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:57:29 2026

@author: paulo.goncalves
"""

import os
import folium
import random
import webbrowser
from mapa_utils import load_coordinates_from_jsonl, generate_service_points
from genetic_algorithm import generate_random_population, evolve_population


WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800

N_POINTS = 15
POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.20

# Centro aproximado de Ceilândia
centro_lat = -15.8219
centro_lon = -48.1072

# Cores por prioridade
priority_colors = {
    1: 'green',
    2: 'blue',
    3: 'orange',
    4: 'red'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    # Carregar coordenadas do dataset
    jsonl_path = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
    coordinates = load_coordinates_from_jsonl(jsonl_path)

    # Gerar pontos de atendimento
    service_points = generate_service_points(coordinates=coordinates, n_points=N_POINTS)

    # Executar GA
    population = generate_random_population(service_points, POPULATION_SIZE)

    generation = 0
    best_route = population[0][:]
    best_fitness = float("inf")

    while generation < 1000:  # Limitar gerações
        generation += 1
        
        population, current_best_route, current_best_fitness = evolve_population(
            population=population,
            population_size=POPULATION_SIZE,
            mutation_probability=MUTATION_PROBABILITY,
            elite_size=1
        )
        
        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_route = current_best_route[:]
        
        print(f"Generation {generation}: Best fitness = {round(best_fitness, 2)}")

    # Criar mapa com Folium
    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)

    # Adicionar marcadores para pontos
    for point in service_points:
        folium.Marker(
            location=[point.lat, point.lon],
            popup=f"Ponto {point.id}: {point.tipo_atendimento} (Prioridade {point.prioridade})",
            icon=folium.Icon(color=priority_colors[point.prioridade])
        ).add_to(mapa)

    # Adicionar rota como polyline
    route_coords = [(point.lat, point.lon) for point in best_route]
    folium.PolyLine(route_coords, color="black", weight=3, opacity=0.8).add_to(mapa)

    # Salvar mapa
    mapa.save("ceilandia_routes.html")
    print("Mapa salvo como ceilandia_routes.html")

    # Abrir no navegador
    webbrowser.open("ceilandia_routes.html")


if __name__ == "__main__":
    main()