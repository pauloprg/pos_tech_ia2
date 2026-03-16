# -*- coding: utf-8 -*-
import sys
import pygame
import os
import folium
import webbrowser
import time
from html2image import Html2Image

from mapa_utils import (
    load_and_scale_map,
    load_coordinates_from_jsonl,
    generate_service_points,
    LAT_MIN, LAT_MAX, LON_MIN, LON_MAX
)
from renderer import draw_route_lines, draw_service_points, draw_side_panel
from genetic_algorithm import generate_random_population, evolve_population

# --- Proporções e Cores ---
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
MAP_WIDTH = 1000
MAP_HEIGHT = 800
PANEL_WIDTH = 400

BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
BLUE_MAIN = (0, 191, 255)

FPS = 30
N_POINTS = 15
POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.25

centro_lat = (LAT_MIN + LAT_MAX) / 2
centro_lon = (LON_MIN + LON_MAX) / 2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_HTML = os.path.join(BASE_DIR, "ceilandia_routes.html")
MAP_PNG = os.path.join(BASE_DIR, "ceilandia_map.png")

def update_map_files(service_points, best_route):
    """Atualiza o mapa Folium com cores mais vivas e gera o PNG."""
    try:
        # Trocando para o estilo padrão colorido do OSM
        # Se o erro 403 voltar, você pode usar "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png" 
        # com o atributo attr="© OpenStreetMap France"
        mapa = folium.Map(
            location=[centro_lat, centro_lon], 
            zoom_start=14, 
            tiles="OpenStreetMap" 
        )
        
        # Cores de prioridade vibrantes para os marcadores
        colors = {4: 'red', 3: 'orange', 2: 'blue', 1: 'green'}
        for p in service_points:
            folium.Marker(
                [p.lat, p.lon], 
                icon=folium.Icon(color=colors.get(p.prioridade, 'blue'), icon='info-sign')
            ).add_to(mapa)
        
        # Rota em Azul Neon com maior opacidade
        route_coords = [(p.lat, p.lon) for p in best_route]
        folium.PolyLine(route_coords, color="#00BFFF", weight=6, opacity=0.9).add_to(mapa)
        
        mapa.save(MAP_HTML)

        hti = Html2Image(custom_flags=['--hide-scrollbars', '--disable-gpu', '--no-sandbox'])
        hti.screenshot(html_file=MAP_HTML, save_as='ceilandia_map.png', size=(MAP_WIDTH, MAP_HEIGHT))
    except Exception as e:
        print(f"Erro ao atualizar mapa vibrante: {e}")

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Dashboard de Saúde da Mulher - Ceilândia")
    clock = pygame.time.Clock()

    t_font = pygame.font.SysFont("arial", 18, bold=True)
    s_font = pygame.font.SysFont("arial", 13)
    xs_font = pygame.font.SysFont("arial", 11)

    jsonl_path = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
    coords = load_coordinates_from_jsonl(jsonl_path)
    service_points = generate_service_points(coords, N_POINTS, MAP_WIDTH, MAP_HEIGHT)
    
    population = generate_random_population(service_points, POPULATION_SIZE)
    generation, best_fitness = 0, float("inf")
    best_route = population[0][:]
    fitness_history, scroll_offset = [], 0

    update_map_files(service_points, best_route)
    map_surface = load_and_scale_map(MAP_PNG, MAP_WIDTH, MAP_HEIGHT)
    
    running = True
    last_map_update = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEWHEEL:
                if pygame.mouse.get_pos()[0] > MAP_WIDTH:
                    scroll_offset = max(0, scroll_offset - event.y * 30)

        generation += 1
        population, cur_best, cur_fit = evolve_population(population, POPULATION_SIZE, MUTATION_PROBABILITY)
        
        if cur_fit < best_fitness:
            best_fitness = cur_fit
            best_route = cur_best[:]
        
        fitness_history.append(best_fitness)
        if len(fitness_history) > 150: fitness_history.pop(0)

        screen.fill(BLACK)
        if map_surface: screen.blit(map_surface, (0, 0))

        # CORREÇÃO: Desenhando estritamente APENAS a melhor rota
        draw_route_lines(screen, best_route)
        draw_service_points(screen, service_points, xs_font)
        
        draw_side_panel(screen, MAP_WIDTH, PANEL_WIDTH, WINDOW_HEIGHT, t_font, s_font, 
                        best_route, generation, best_fitness, fitness_history, scroll_offset)

        pygame.display.flip()
        clock.tick(FPS)

        if pygame.time.get_ticks() - last_map_update > 60000:
            update_map_files(service_points, best_route)
            map_surface = load_and_scale_map(MAP_PNG, MAP_WIDTH, MAP_HEIGHT)
            last_map_update = pygame.time.get_ticks()

    pygame.quit()

if __name__ == "__main__":
    main()