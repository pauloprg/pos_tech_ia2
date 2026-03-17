# -*- coding: utf-8 -*-
"""
Pygame visualization for Ceilândia routes
"""

import sys
import pygame
import os

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
from genetic_algorithm import calculate_total_distance_km

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800

MAP_WIDTH = 980
MAP_HEIGHT = 800
PANEL_WIDTH = WINDOW_WIDTH - MAP_WIDTH

FPS = 10
N_POINTS = 15

POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.20

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(BASE_DIR, "assets", "Mapa_Ceilandia.png")

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Saúde da Mulher em Ceilândia")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arial", 20, bold=True)
    text_font = pygame.font.SysFont("arial", 11)
    small_font = pygame.font.SysFont("arial", 10)

    map_surface = load_and_scale_map(MAP_PATH, MAP_WIDTH, MAP_HEIGHT)
    coordinates = load_coordinates_from_jsonl(os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl"))

    service_points = generate_service_points(coordinates=coordinates,
        n_points=N_POINTS)
    
    population = generate_random_population(service_points, POPULATION_SIZE)
    
    generation = 0
    best_route = population[0][:]
    best_fitness = float("inf")
    fitness_history = []
    scroll_offset = 0
    max_scroll = 0
    
    panel_rect = pygame.Rect(MAP_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)

    running = True
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
        
        fitness_history.append(best_fitness)
        if len(fitness_history) > 300:
            fitness_history = fitness_history[-300:]
            
        print(f"Generation {generation}: Best fitness = {round(best_fitness, 2)}")
        
        screen.fill((255, 255, 255))
        screen.blit(map_surface, (0, 0))

        draw_route_lines(screen, best_route)
        # Usa a melhor rota para numerar os pontos na ordem visitada
        draw_service_points(screen, best_route if best_route else service_points, small_font)
        
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
            dist_km=calculate_total_distance_km(best_route),
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

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()