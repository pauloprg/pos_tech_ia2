# -*- coding: utf-8 -*-
import sys, pygame, os
from mapa_utils import *
from renderer import *
from genetic_algorithm import *
from ai_advisor import *

WINDOW_WIDTH, WINDOW_HEIGHT = 1400, 800
MAP_WIDTH, PANEL_WIDTH = 1000, 400
FPS = 30 # Definido globalmente

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Saúde da Mulher - Ceilândia")
    clock = pygame.time.Clock()
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
    
    coords_data = load_coordinates_from_jsonl(json_path)
    service_points = generate_service_points(coords_data, 15, MAP_WIDTH, WINDOW_HEIGHT)
    
    population = generate_random_population(service_points, 100)
    best_fitness = float("inf")
    fitness_history = []
    generation, stable_count, is_optimal = 0, 0, False
    popup = None
    best_route = []

    try:
        map_surface = load_and_scale_map(os.path.join(BASE_DIR, "mapa_vibrante.png"), MAP_WIDTH, WINDOW_HEIGHT)
    except:
        map_surface = None

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if popup and popup.visivel:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: popup.visivel = False
                    elif event.key == pygame.K_RETURN:
                        if popup.input_usuario.strip():
                            msg = popup.input_usuario
                            popup.input_usuario = ""
                            popup.carregando = True
                            popup.draw(screen); pygame.display.flip()
                            res = enviar_mensagem_chat(msg)
                            popup.adicionar_mensagem("Maitê", msg)
                            popup.adicionar_mensagem("IA", res)
                    elif event.key == pygame.K_BACKSPACE: popup.input_usuario = popup.input_usuario[:-1]
                    else: popup.input_usuario += event.unicode
                continue 

            if event.type == pygame.MOUSEBUTTONDOWN:
                btn_rect = pygame.Rect(MAP_WIDTH + 50, 530, 300, 45)
                if btn_rect.collidepoint(mouse_pos) and is_optimal:
                    if not popup:
                        briefing = gerar_briefing_vibrante(best_route)
                        inicializar_chat(best_route)
                        popup = BriefingPopup(briefing)
                    else: popup.visivel = True

        if not is_optimal:
            generation += 1
            population, cur_best, cur_fit = evolve_population(population, 100, 0.25)
            if cur_fit < best_fitness:
                best_fitness, best_route, stable_count = cur_fit, cur_best[:], 0
            else: stable_count += 1
            if stable_count > 500: is_optimal = True
            fitness_history.append(best_fitness)
            if len(fitness_history) > 150: fitness_history.pop(0)

        screen.fill(BLACK)
        if map_surface: screen.blit(map_surface, (0, 0))
        draw_route_lines(screen, best_route)
        draw_service_points(screen, service_points, pygame.font.SysFont("arial", 11))
        draw_side_panel(screen, MAP_WIDTH, PANEL_WIDTH, WINDOW_HEIGHT, 
                        pygame.font.SysFont("arial", 18, True), pygame.font.SysFont("arial", 13),
                        best_route, generation, best_fitness, fitness_history, 0, is_optimal)
        draw_chat_button(screen, MAP_WIDTH + 50, 530, 300, 45, is_optimal)
        if popup and popup.visivel: popup.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()