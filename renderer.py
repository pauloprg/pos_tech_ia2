# -*- coding: utf-8 -*-
import pygame
from pontos import ServicePoint
from typing import List

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE_MAIN = (0, 191, 255)
PANEL_BG = (25, 25, 25)
GRAY_TEXT = (170, 170, 170)

PRIORITY_COLORS = {
    4: (255, 50, 50), 3: (255, 165, 0), 2: (0, 200, 255), 1: (50, 255, 50)
}

def draw_route_lines(screen, route):
    if len(route) < 2: return
    for i in range(len(route) - 1):
        p1, p2 = (route[i].x, route[i].y), (route[i+1].x, route[i+1].y)
        
        # Efeito de linha dupla para maior visibilidade sobre o mapa colorido
        pygame.draw.line(screen, (255, 255, 255), p1, p2, 5) # Borda branca de contraste
        pygame.draw.line(screen, (0, 191, 255), p1, p2, 3)   # Centro Ciano Vibrante
        pygame.draw.circle(screen, WHITE, p1, 3)

def draw_service_points(screen, points, font):
    for point in points:
        color = PRIORITY_COLORS.get(point.prioridade, WHITE)
        pygame.draw.circle(screen, color, (point.x, point.y), 9)
        pygame.draw.circle(screen, WHITE, (point.x, point.y), 9, 2)
        lbl = font.render(f"P{point.id}", True, WHITE)
        bg_rect = lbl.get_rect(center=(point.x, point.y - 18))
        pygame.draw.rect(screen, BLACK, bg_rect.inflate(4, 2))
        screen.blit(lbl, bg_rect)

def draw_side_panel(screen, panel_x, panel_width, window_height, title_font, text_font, 
                    route, generation, best_fitness, fitness_history, scroll_offset):
    
    pygame.draw.rect(screen, PANEL_BG, (panel_x, 0, panel_width, window_height))
    pygame.draw.line(screen, BLUE_MAIN, (panel_x, 0), (panel_x, window_height), 2)

    margin = panel_x + 20
    screen.blit(title_font.render("FINETUNE EM TEMPO REAL", True, BLUE_MAIN), (margin, 20))
    screen.blit(text_font.render(f"Geração: {generation}", True, WHITE), (margin, 55))
    screen.blit(text_font.render(f"Melhor Distância: {round(best_fitness, 2)} km", True, WHITE), (margin, 75))

    y_list = 110 - scroll_offset
    for i, p in enumerate(route):
        if 110 < y_list < 580:
            pygame.draw.rect(screen, PRIORITY_COLORS.get(p.prioridade), (margin, y_list + 4, 6, 12))
            screen.blit(text_font.render(f"{i+1}º -> Ponto {p.id}", True, WHITE), (margin + 15, y_list))
        y_list += 22

    # --- GRÁFICO COM EIXOS ---
    graph_x, graph_y, graph_w, graph_h = margin + 35, 620, panel_width - 75, 140
    pygame.draw.rect(screen, (10, 10, 10), (graph_x, graph_y, graph_w, graph_h))
    pygame.draw.line(screen, WHITE, (graph_x, graph_y), (graph_x, graph_y + graph_h), 2)
    pygame.draw.line(screen, WHITE, (graph_x, graph_y + graph_h), (graph_x + graph_w, graph_y + graph_h), 2)

    if len(fitness_history) > 2:
        max_f, min_f = max(fitness_history), min(fitness_history)
        rng = max_f - min_f if max_f != min_f else 1
        
        # Valores dos Eixos
        screen.blit(text_font.render(f"{int(max_f)}", True, GRAY_TEXT), (margin - 5, graph_y))
        screen.blit(text_font.render(f"{int(min_f)}", True, GRAY_TEXT), (margin - 5, graph_y + graph_h - 15))
        
        pts = [(graph_x + (i * graph_w / len(fitness_history)), 
                (graph_y + graph_h) - ((f - min_f) / rng * (graph_h - 10))) 
               for i, f in enumerate(fitness_history)]
        pygame.draw.lines(screen, BLUE_MAIN, False, pts, 2)

    return y_list