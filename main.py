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

# --- Configurações de Interface ---
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
MAP_WIDTH = 1000
MAP_HEIGHT = 800
PANEL_WIDTH = 400

BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
FPS = 30

def update_map_background(service_points, BASE_DIR):
    """Gera o fundo do mapa com marcadores vibrantes, SEM a rota desenhada."""
    try:
        centro_lat = (LAT_MIN + LAT_MAX) / 2
        centro_lon = (LON_MIN + LON_MAX) / 2
        
        # Tiles do Google para cores vibrantes
        mapa = folium.Map(
            location=[centro_lat, centro_lon], 
            zoom_start=14, 
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", 
            attr="Google"
        )
        
        colors = {4: 'red', 3: 'orange', 2: 'blue', 1: 'green'}
        for p in service_points:
            folium.Marker(
                [p.lat, p.lon], 
                icon=folium.Icon(color=colors.get(p.prioridade, 'blue'), icon='info-sign')
            ).add_to(mapa)
        
        map_path = os.path.join(BASE_DIR, "temp_map.html")
        mapa.save(map_path)

        hti = Html2Image(custom_flags=['--hide-scrollbars', '--disable-gpu', '--no-sandbox'])
        hti.screenshot(html_file=map_path, save_as='ceilandia_map.png', size=(MAP_WIDTH, MAP_HEIGHT))
    except Exception as e:
        print(f"Erro ao gerar fundo do mapa: {e}")

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Saúde da Mulher - Dashboard Ceilândia")
    clock = pygame.time.Clock()

    # Fontes
    font_title = pygame.font.SysFont("arial", 18, bold=True)
    font_text = pygame.font.SysFont("arial", 13)
    font_small = pygame.font.SysFont("arial", 11)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
    coords = load_coordinates_from_jsonl(json_path)
    
    # Gera pontos concentrados no centro
    service_points = generate_service_points(coords, 15, MAP_WIDTH, MAP_HEIGHT)
    
    population = generate_random_population(service_points, 100)
    best_route = population[0][:]
    best_fitness = float("inf")
    fitness_history = []
    
    # Lógica de Geração Ótima
    stable_generations = 0
    is_optimal = False
    generation = 0

    update_map_background(service_points, BASE_DIR)
    map_surface = load_and_scale_map(os.path.join(BASE_DIR, "ceilandia_map.png"), MAP_WIDTH, MAP_HEIGHT)

    running = True
    scroll_offset = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEWHEEL:
                if pygame.mouse.get_pos()[0] > MAP_WIDTH:
                    scroll_offset = max(0, scroll_offset - event.y * 30)

        # Evolução do Algoritmo
        generation += 1
        population, cur_best, cur_fit = evolve_population(population, 100, 0.25)
        
        if cur_fit < best_fitness:
            best_fitness = cur_fit
            best_route = cur_best[:]
            stable_generations = 0
        else:
            stable_generations += 1
        
        # Define como ótima se não houver melhora por 500 gerações
        if stable_generations > 500: is_optimal = True
        
        fitness_history.append(best_fitness)
        if len(fitness_history) > 150: fitness_history.pop(0)

        # Renderização
        screen.fill(BLACK)
        if map_surface: screen.blit(map_surface, (0, 0))

        # Desenha APENAS a rota principal (sem duplicatas)
        draw_route_lines(screen, best_route)
        draw_service_points(screen, service_points, font_small)
        
        # Painel lateral com Gráfico e Rótulos X,Y
        draw_side_panel(screen, MAP_WIDTH, PANEL_WIDTH, WINDOW_HEIGHT, font_title, font_text, 
                        best_route, generation, best_fitness, fitness_history, scroll_offset, is_optimal)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()