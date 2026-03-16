# -*- coding: utf-8 -*-
import sys
import pygame
import os
import folium
import webbrowser
import time
from html2image import Html2Image

# Importações dos seus módulos locais
from mapa_utils import (
    load_and_scale_map,
    load_coordinates_from_jsonl,
    generate_service_points,
    LAT_MIN, LAT_MAX, LON_MIN, LON_MAX
)
from renderer import draw_route_lines, draw_service_points, draw_side_panel
from genetic_algorithm import (
    generate_random_population,
    evolve_population
)

# --- Configurações de Interface ---
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
MAP_WIDTH = 980
MAP_HEIGHT = 800
PANEL_WIDTH = WINDOW_WIDTH - MAP_WIDTH

# --- Parâmetros do Sistema ---
FPS = 10
N_POINTS = 15
POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.20

# Centro da Ceilândia para o mapa interativo
centro_lat = (LAT_MIN + LAT_MAX) / 2
centro_lon = (LON_MIN + LON_MAX) / 2

# Cores para o Folium
priority_colors_folium = {
    1: 'green',
    2: 'blue',
    3: 'orange',
    4: 'red'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_HTML = os.path.join(BASE_DIR, "ceilandia_routes.html")
MAP_PNG = os.path.join(BASE_DIR, "ceilandia_map.png")

def create_folium_map(service_points, best_route, generation, best_fitness):
    """Cria o mapa Folium e exporta para HTML e PNG."""
    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=14, tiles="openstreetmap")

    # Marcadores dos 15 pontos
    for point in service_points:
        folium.Marker(
            location=[point.lat, point.lon],
            popup=f"Ponto {point.id}: {point.tipo_atendimento}",
            icon=folium.Icon(color=priority_colors_folium[point.prioridade], icon='info-sign')
        ).add_to(mapa)

    # Linha da Melhor Rota
    route_coords = [(p.lat, p.lon) for p in best_route]
    folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.7).add_to(mapa)

    # Salva o arquivo HTML com meta-tag de atualização automática (refresh)
    html_content = mapa.get_root().render()
    html_content = html_content.replace('<head>', '<head><meta http-equiv="refresh" content="10">')
    
    with open(MAP_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Tenta gerar a imagem PNG para o fundo do Pygame
    try:
        hti = Html2Image(custom_flags=['--hide-scrollbars', '--disable-gpu', '--no-sandbox'])
        hti.screenshot(html_file=MAP_HTML, save_as='ceilandia_map.png', size=(MAP_WIDTH, MAP_HEIGHT))
    except Exception as e:
        print(f"Aviso: Não foi possível atualizar o fundo PNG: {e}")

def main():
    # 1. Inicialização de Controle
    running = True
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Saúde da Mulher - Otimização de Rotas (Ceilândia)")
    clock = pygame.time.Clock()

    # Fontes
    title_font = pygame.font.SysFont("arial", 20, bold=True)
    text_font = pygame.font.SysFont("arial", 12)
    small_font = pygame.font.SysFont("arial", 10)

    # 2. Preparação de Dados
    jsonl_path = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
    coordinates = load_coordinates_from_jsonl(jsonl_path)
    
    # Gera exatamente os 15 pontos na área da Ceilândia
    service_points = generate_service_points(
        coordinates=coordinates, 
        n_points=N_POINTS, 
        map_width=MAP_WIDTH, 
        map_height=MAP_HEIGHT
    )
    
    # 3. Inicialização do Algoritmo Genético
    population = generate_random_population(service_points, POPULATION_SIZE)
    generation = 0
    best_route = population[0][:]
    best_fitness = float("inf")
    fitness_history = []
    scroll_offset = 0
    
    # 4. Mapa Inicial e Visualização Web
    create_folium_map(service_points, best_route, generation, best_fitness)
    webbrowser.open(MAP_HTML)
    
    # Pequena pausa para garantir que a imagem PNG foi criada antes do primeiro blit
    time.sleep(2)
    map_surface = load_and_scale_map(MAP_PNG, MAP_WIDTH, MAP_HEIGHT)
    
    panel_rect = pygame.Rect(MAP_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)

    # --- Loop Principal ---
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                if panel_rect.collidepoint(pygame.mouse.get_pos()):
                    scroll_offset -= event.y * 25
                    scroll_offset = max(0, scroll_offset)

        # Evolução do AG
        generation += 1
        population, current_best_route, current_best_fitness = evolve_population(
            population=population,
            population_size=POPULATION_SIZE,
            mutation_probability=MUTATION_PROBABILITY,
            elite_size=2
        )
        
        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_route = current_best_route[:]
        
        fitness_history.append(best_fitness)
        if len(fitness_history) > 200: fitness_history.pop(0)

        # --- Renderização ---
        screen.fill((255, 255, 255))
        
        # Desenha o mapa de fundo (vindo do Folium)
        screen.blit(map_surface, (0, 0))

        # Desenha rotas e pontos (Renderer)
        draw_route_lines(screen, best_route)
        draw_service_points(screen, service_points, small_font)
        
        # Desenha o painel lateral com informações
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

        pygame.display.flip()
        clock.tick(FPS)

        # Atualiza o arquivo HTML e PNG periodicamente (a cada 30 gerações)
        if generation % 30 == 0:
            create_folium_map(service_points, best_route, generation, best_fitness)
            # Recarrega a imagem para o Pygame
            map_surface = load_and_scale_map(MAP_PNG, MAP_WIDTH, MAP_HEIGHT)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()