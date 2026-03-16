# -*- coding: utf-8 -*-
import sys, pygame, os, folium, time
from html2image import Html2Image
from mapa_utils import load_and_scale_map, load_coordinates_from_jsonl, generate_service_points, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX
from renderer import draw_route_lines, draw_service_points, draw_side_panel
from genetic_algorithm import generate_random_population, evolve_population

WINDOW_WIDTH, WINDOW_HEIGHT = 1400, 800
MAP_WIDTH, PANEL_WIDTH = 1000, 800 # Sincronizado com a altura
FPS = 30

def update_map_files(service_points, best_route, BASE_DIR):
    """Gera um mapa LIMPO sem ícones redundantes."""
    try:
        # 1. Limpa arquivos antigos para evitar carregar imagem velha
        img_path = os.path.join(BASE_DIR, "mapa_vibrante.png")
        html_path = os.path.join(BASE_DIR, "mapa_temp.html")
        if os.path.exists(img_path): os.remove(img_path)

        # 2. Criar mapa usando Google Maps (Vibrante)
        mapa = folium.Map(
            location=[(LAT_MIN+LAT_MAX)/2, (LON_MIN+LON_MAX)/2], 
            zoom_start=14, 
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", 
            attr="Google"
        )
        
        # NOTA: Removido folium.Marker para não duplicar ícones na tela
        mapa.save(html_path)

        # 3. Screenshot (Gera um fundo novo e limpo)
        hti = Html2Image(custom_flags=['--hide-scrollbars', '--disable-gpu', '--no-sandbox'])
        hti.screenshot(html_file=html_path, save_as="mapa_vibrante.png", size=(MAP_WIDTH, WINDOW_HEIGHT))
        return True
    except Exception as e:
        print(f"Erro no mapa: {e}")
        return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Otimização Real-Time Ceilândia")
    clock = pygame.time.Clock()
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    coords = load_coordinates_from_jsonl(os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl"))
    service_points = generate_service_points(coords, 15, MAP_WIDTH, WINDOW_HEIGHT)
    
    population = generate_random_population(service_points, 100)
    best_route, best_fitness, generation = population[0][:], float("inf"), 0
    fitness_history, stable_count = [], 0
    is_optimal = False
    
    print("Gerando novo fundo limpo...")
    update_map_files(service_points, best_route, BASE_DIR)
    map_surface = load_and_scale_map(os.path.join(BASE_DIR, "mapa_vibrante.png"), MAP_WIDTH, WINDOW_HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        generation += 1
        population, cur_best, cur_fit = evolve_population(population, 100, 0.25)
        
        if cur_fit < best_fitness:
            best_fitness, best_route = cur_fit, cur_best[:]
            stable_count = 0
        else: stable_count += 1
        
        if stable_count > 500: is_optimal = True
        fitness_history.append(best_fitness)
        if len(fitness_history) > 150: fitness_history.pop(0)

        # DESENHO
        screen.fill((20,20,20))
        if map_surface: screen.blit(map_surface, (0, 0)) # Fundo limpo
        
        draw_route_lines(screen, best_route) # Rota única e fina
        draw_service_points(screen, service_points, pygame.font.SysFont("arial", 11)) # Pontos Pygame
        
        draw_side_panel(screen, MAP_WIDTH, PANEL_WIDTH, WINDOW_HEIGHT, 
                        pygame.font.SysFont("arial", 18, True), pygame.font.SysFont("arial", 13),
                        best_route, generation, best_fitness, fitness_history, 0, is_optimal)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()