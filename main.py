# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:57:29 2026

@author: paulo.goncalves
"""

import sys
import pygame
import os
import folium
import random
import webbrowser
from html2image import Html2Image
from mapa_utils import (
    load_and_scale_map,
    load_coordinates_from_jsonl,
    generate_service_points
)
from renderer import draw_route_lines, draw_service_points, draw_side_panel
from genetic_algorithm import (
    generate_random_population,
    evolve_population
)


WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800

MAP_WIDTH = 980
MAP_HEIGHT = 800
PANEL_WIDTH = WINDOW_WIDTH - MAP_WIDTH

FPS = 10
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

# Caminho para a imagem do mapa (gerada dinamicamente)
MAP_PATH = "ceilandia_map.png"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(BASE_DIR, "assets", "Mapa_Ceilandia.png")


def main():
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Saúde da Mulher em Ceilândia")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arial", 20, bold=True)
    text_font = pygame.font.SysFont("arial", 11)
    small_font = pygame.font.SysFont("arial", 10)

    # Carregar mapa para Pygame
    map_surface = load_and_scale_map(MAP_PATH, MAP_WIDTH, MAP_HEIGHT)
    
    # Carregar coordenadas
    jsonl_path = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
    coordinates = load_coordinates_from_jsonl(jsonl_path)

    # Gerar pontos
    service_points = generate_service_points(coordinates=coordinates, n_points=N_POINTS)
    
    # Inicializar GA
    population = generate_random_population(service_points, POPULATION_SIZE)
    
    generation = 0
    best_route = population[0][:]
    best_fitness = float("inf")
    fitness_history = []
    scroll_offset = 0
    max_scroll = 0
    generations_without_improvement = 0
    max_generations_without_improvement = 100  # Parar se não melhorar por 100 gerações
    
    panel_rect = pygame.Rect(MAP_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)

    # Criar mapa inicial e imagem
    create_folium_map(service_points, best_route, generation, best_fitness)
    
    # Aguardar a geração da imagem
    import time
    time.sleep(3)
    
    # Carregar mapa para Pygame (usando imagem gerada)
    map_surface = load_and_scale_map(MAP_PATH, MAP_WIDTH, MAP_HEIGHT)
    
    # Abrir navegador com mapa inicial
    webbrowser.open("ceilandia_routes.html")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if panel_rect.collidepoint(mouse_x, mouse_y):
                    scroll_offset -= event.y * 25
                    if scroll_offset < 0:
                        scroll_offset = 0
                    if scroll_offset > max_scroll:
                        scroll_offset = max_scroll
                
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
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1
        
        fitness_history.append(best_fitness)
        if len(fitness_history) > 300:
            fitness_history = fitness_history[-300:]
            
        print(f"Generation {generation}: Best fitness = {round(best_fitness, 2)}")
        
        # Parar se não houver melhoria por muitas gerações
        if generations_without_improvement >= max_generations_without_improvement:
            print(f"Convergência alcançada após {generation} gerações. Melhor fitness: {round(best_fitness, 2)}")
            break
        
        # Atualizar Pygame
        screen.fill((255, 255, 255))
        screen.blit(map_surface, (0, 0))

        draw_route_lines(screen, best_route)
        draw_service_points(screen, service_points, small_font)
        
        max_scroll = draw_side_panel(
            screen=screen,
            panel_x=MAP_WIDTH,
            panel_width=PANEL_WIDTH,
            window_height=WINDOW_HEIGHT,
            title_font=title_font,
            text_font=text_font,
            route=best_route,
            generation=generation,
            best_fitness=best_fitness,
            fitness_history=fitness_history,
            scroll_offset=scroll_offset
        )
        
        if scroll_offset > max_scroll:
            scroll_offset = max_scroll

        footer = text_font.render(
            "Tech Challenge fase 2: otimização de rotas em Ceilândia com algoritmo genético",
            True,
            (20, 20, 20)
        )
        screen.blit(footer, (20, WINDOW_HEIGHT - 22))

        pygame.display.flip()
        clock.tick(FPS)

        # Atualizar Folium a cada 10 gerações
        if generation % 10 == 0:
            create_folium_map(service_points, best_route, generation, best_fitness)

    pygame.quit()
    sys.exit()


def create_folium_map(service_points, best_route, generation, best_fitness):
    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)

    # Adicionar marcadores
    for point in service_points:
        folium.Marker(
            location=[point.lat, point.lon],
            popup=f"Ponto {point.id}: {point.tipo_atendimento} (Prioridade {point.prioridade})",
            icon=folium.Icon(color=priority_colors[point.prioridade])
        ).add_to(mapa)

    # Adicionar rota
    route_coords = [(point.lat, point.lon) for point in best_route]
    folium.PolyLine(route_coords, color="black", weight=3, opacity=0.8).add_to(mapa)

    # Adicionar info da geração
    folium.Marker(
        location=[centro_lat + 0.01, centro_lon + 0.01],
        popup=f"Geração: {generation}, Fitness: {round(best_fitness, 2)}",
        icon=folium.Icon(color="purple", icon="info-sign")
    ).add_to(mapa)

    # Salvar com auto-refresh
    html_content = mapa.get_root().render()
    html_content = html_content.replace('<head>', '<head><meta http-equiv="refresh" content="5">')
    
    with open("ceilandia_routes.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # Gerar imagem do mapa
    generate_map_image()


def generate_map_image():
    """Gera uma imagem PNG do mapa Folium usando html2image"""
    try:
        hti = Html2Image()
        hti.screenshot(
            html_file='ceilandia_routes.html',
            save_as='ceilandia_map.png',
            size=(980, 800)
        )
        print("Imagem do mapa gerada: ceilandia_map.png")
        
    except Exception as e:
        print(f"Erro ao gerar imagem do mapa: {e}")
        # Fallback: usar imagem existente se houver
        if os.path.exists(os.path.join(BASE_DIR, "assets", "Mapa_Ceilandia.png")):
            import shutil
            shutil.copy(os.path.join(BASE_DIR, "assets", "Mapa_Ceilandia.png"), "ceilandia_map.png")


if __name__ == "__main__":
    main()