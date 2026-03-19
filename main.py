# main.py
# -*- coding: utf-8 -*-

import os
import sys
import pygame

from ai_advisor import enviar_mensagem_chat, gerar_roteiro_inteligente, inicializar_chat
from mapa_utils import (
    build_default_depot,
    build_default_fleet,
    generate_service_points,
    load_and_scale_map,
    load_coordinates_from_jsonl,
)
from renderer import (
    BLACK,
    BriefingPopup,
    draw_chat_button,
    draw_convergence_graph,
    draw_service_points,
    draw_side_panel,
)
from vrp_genetic import evolve_population, generate_random_population

WINDOW_WIDTH, WINDOW_HEIGHT = 1400, 750
MAP_WIDTH = 850
PANEL_WIDTH = 550
FPS = 25


def draw_vehicle_routes(screen, depot, routes):
    colors = [
        (255, 80, 80),
        (80, 180, 255),
        (80, 220, 120),
        (240, 200, 80),
        (200, 120, 255),
        (255, 140, 80),
    ]

    for idx, route in enumerate(routes):
        color = colors[idx % len(colors)]
        if not route.points:
            continue

        points = [(depot.x, depot.y)] + [p.posicao() for p in route.points] + [(depot.x, depot.y)]
        pygame.draw.lines(screen, color, False, points, 3)


def flatten_best_points(routes):
    result = []
    for route in routes:
        result.extend(route.points)
    return result


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Saúde da Mulher - VRP com Frota Heterogênea")
    clock = pygame.time.Clock()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "assets", "dataset_ceilandia_osm.jsonl")

    coords_data = load_coordinates_from_jsonl(json_path)
    service_points = generate_service_points(coords_data, 18, MAP_WIDTH, WINDOW_HEIGHT)

    fleet = build_default_fleet()
    depot = build_default_depot(MAP_WIDTH, WINDOW_HEIGHT)

    population = generate_random_population(service_points, 120)

    best_solution = None
    fitness_history = []
    generation = 0
    stable_count = 0
    is_optimal = False
    popup = None

    try:
        map_surface = load_and_scale_map(
            os.path.join(base_dir, "mapa_vibrante.png"),
            MAP_WIDTH,
            WINDOW_HEIGHT
        )
    except Exception:
        map_surface = None

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if popup and popup.visivel:
                popup.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        popup.visivel = False
                    elif event.key == pygame.K_RETURN:
                        if popup.input_usuario.strip():
                            msg = popup.input_usuario
                            popup.input_usuario = ""
                            popup.carregando = True
                            popup.draw(screen)
                            pygame.display.flip()
                            res = enviar_mensagem_chat(msg)
                            popup.carregando = False
                            popup.adicionar_mensagem("Gerreiro", msg)
                            popup.adicionar_mensagem("IA", res)
                    elif event.key == pygame.K_BACKSPACE:
                        popup.input_usuario = popup.input_usuario[:-1]
                    else:
                        if event.unicode and event.key not in (pygame.K_RETURN, pygame.K_ESCAPE):
                            popup.input_usuario += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                btn_rect = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H)

                if btn_rect.collidepoint(mouse_pos) and is_optimal and best_solution:
                    resumo_llm = []
                    for route in best_solution.routes:
                        resumo_llm.append({
                            "veiculo": route.vehicle.nome,
                            "tipo": route.vehicle.tipo,
                            "distancia_km": round(route.total_distance_km, 2),
                            "paradas": route.total_stops,
                            "carga": route.total_load,
                            "atendimentos": [
                                {
                                    "codigo": p.codigo,
                                    "tipo": p.tipo_atendimento,
                                    "prioridade": p.prioridade,
                                }
                                for p in route.points
                            ]
                        })

                    briefing = gerar_roteiro_inteligente(resumo_llm)
                    inicializar_chat(resumo_llm)
                    popup = BriefingPopup(briefing)

        if not is_optimal:
            generation += 1
            population, current_best = evolve_population(
                population=population,
                vehicles=fleet,
                depot=depot,
                pop_size=120,
                mutation_rate=0.25,
                elite_ratio=0.2,
            )

            if best_solution is None or current_best.fitness < best_solution.fitness:
                best_solution = current_best
                stable_count = 0
            else:
                stable_count += 1

            if stable_count > 250:
                is_optimal = True

            fitness_history.append(best_solution.fitness)
            if len(fitness_history) > 150:
                fitness_history.pop(0)

        screen.fill(BLACK)
        if map_surface:
            screen.blit(map_surface, (0, 0))

        if best_solution:
            draw_vehicle_routes(screen, depot, best_solution.routes)
            draw_service_points(
                screen,
                flatten_best_points(best_solution.routes),
                pygame.font.SysFont("arial", 11)
            )

            total_distance = sum(r.total_distance_km for r in best_solution.routes)
            draw_side_panel(
                screen,
                MAP_WIDTH,
                PANEL_WIDTH,
                WINDOW_HEIGHT,
                pygame.font.SysFont("arial", 18, True),
                pygame.font.SysFont("arial", 13),
                flatten_best_points(best_solution.routes),
                generation,
                best_solution.fitness,
                total_distance,
                fitness_history,
                0,
                is_optimal,
            )

        BUTTON_X = MAP_WIDTH + 40
        BUTTON_Y = WINDOW_HEIGHT - 265
        BUTTON_W = PANEL_WIDTH - 80
        BUTTON_H = 44

        btn_rect = draw_chat_button(screen, BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H, is_optimal)

        GRAPH_X = MAP_WIDTH + 28
        GRAPH_Y = WINDOW_HEIGHT - 190
        GRAPH_W = PANEL_WIDTH - 80
        GRAPH_H = 140

        if not (popup and popup.visivel):
            draw_convergence_graph(screen, GRAPH_X, GRAPH_Y, GRAPH_W, GRAPH_H, fitness_history)

        if popup and popup.visivel:
            popup.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()