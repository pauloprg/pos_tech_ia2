# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:57:29 2026

@author: paulo.goncalves
"""

import sys
import pygame
import os

from mapa_utils import (
    load_and_scale_map,
    build_valid_positions,
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

FPS = 15
N_POINTS = 50

POPULATION_SIZE = 120
MUTATION_PROBABILITY = 0.20

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(BASE_DIR, "assets", "Mapa_DF.png")


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Saúde da Mulher no DF - Roteirização Inicial")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arial", 20, bold=True)
    text_font = pygame.font.SysFont("arial", 10)
    small_font = pygame.font.SysFont("arial", 11)

    map_surface = load_and_scale_map(MAP_PATH, MAP_WIDTH, MAP_HEIGHT)
    valid_positions = build_valid_positions(map_surface)

    service_points = generate_service_points(valid_positions=valid_positions,
        n_points=N_POINTS)
#    current_route = create_initial_route(service_points)
    
    population = generate_random_population(service_points, POPULATION_SIZE)
    generation = 0
    best_route = population[0][:]
    best_fitness = float("inf")


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
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
        
        screen.fill((255, 255, 255))
        screen.blit(map_surface, (0, 0))

        draw_route_lines(screen, best_route)
        draw_service_points(screen, service_points, small_font)
        draw_side_panel(
            screen=screen,
            panel_x=MAP_WIDTH,
            panel_width=PANEL_WIDTH,
            window_height=WINDOW_HEIGHT,
            title_font=title_font,
            text_font=text_font,
            route=best_route,
            generation=generation,
            best_fitness=best_fitness
        )

        footer = text_font.render(
            "Tech 2: otimização de rotas com algoritmo genético",
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