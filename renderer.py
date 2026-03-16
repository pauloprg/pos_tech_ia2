# -*- coding: utf-8 -*-
import pygame
from pontos import ServicePoint
from typing import List

# Cores do Dashboard
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE_MAIN = (0, 191, 255)
GOLD = (255, 215, 0)
GRAY_L = (170, 170, 170)
PANEL_BG = (25, 25, 25)

PRIORITY_COLORS = {
    4: (255, 50, 50),   # Vermelho
    3: (255, 165, 0),   # Laranja
    2: (0, 200, 255),   # Ciano
    1: (50, 255, 50)    # Verde
}

def draw_route_lines(screen, route):
    """Desenha APENAS a melhor rota em tempo real."""
    if len(route) < 2: return
    for i in range(len(route) - 1):
        p1 = (route[i].x, route[i].y)
        p2 = (route[i+1].x, route[i+1].y)
        pygame.draw.line(screen, BLUE_MAIN, p1, p2, 3)
        pygame.draw.circle(screen, WHITE, p1, 2)

def draw_service_points(screen, points, font):
    """Desenha os pontos no mapa."""
    for p in points:
        color = PRIORITY_COLORS.get(p.prioridade, WHITE)
        pygame.draw.circle(screen, color, (p.x, p.y), 8)
        pygame.draw.circle(screen, WHITE, (p.x, p.y), 8, 2)
        lbl = font.render(f"P{p.id}", True, WHITE)
        bg_rect = lbl.get_rect(center=(p.x, p.y - 15))
        pygame.draw.rect(screen, BLACK, bg_rect.inflate(4, 2))
        screen.blit(lbl, bg_rect)

def draw_side_panel(screen, panel_x, panel_width, window_height, title_font, text_font, 
                    route, generation, best_fitness, fitness_history, scroll_offset, is_optimal=False):
    
    # 1. Desenha o Fundo do Painel (Importante: panel_x deve ser 1000)
    pygame.draw.rect(screen, PANEL_BG, (panel_x, 0, panel_width, window_height))
    pygame.draw.line(screen, BLUE_MAIN, (panel_x, 0), (panel_x, window_height), 3)

    margin = panel_x + 20
    
    # 2. Cabeçalho de Status
    color_status = GOLD if is_optimal else BLUE_MAIN
    txt_status = "GERAÇÃO ÓTIMA!" if is_optimal else f"GERAÇÃO: {generation}"
    
    screen.blit(title_font.render(txt_status, True, color_status), (margin, 20))
    screen.blit(text_font.render(f"Distância: {round(best_fitness, 2)} km", True, WHITE), (margin, 50))

    # 3. Lista de Atendimento (Labels) - Verifique se o scroll_offset não está muito alto
    y_list = 100 - scroll_offset
    for i, p in enumerate(route):
        # Clipping: Só desenha se estiver dentro da área útil do painel
        if 90 < y_list < 580:
            prio_color = PRIORITY_COLORS.get(p.prioridade, WHITE)
            # Marcador de cor da prioridade
            pygame.draw.rect(screen, prio_color, (margin, y_list + 3, 6, 12))
            # Texto do rótulo
            label_text = f"{i+1}º -> Ponto {p.id} (Prio {p.prioridade})"
            screen.blit(text_font.render(label_text, True, WHITE), (margin + 15, y_list))
        y_list += 22

    # 4. Gráfico de Finetune com Eixos X, Y
    gx, gy, gw, gh = panel_x + 45, 620, panel_width - 80, 140
    pygame.draw.rect(screen, (10, 10, 10), (gx, gy, gw, gh))
    pygame.draw.line(screen, WHITE, (gx, gy), (gx, gy + gh), 2) # Eixo Y
    pygame.draw.line(screen, WHITE, (gx, gy + gh), (gx + gw, gy + gh), 2) # Eixo X

    if len(fitness_history) > 2:
        max_f, min_f = max(fitness_history), min(fitness_history)
        rng = max_f - min_f if max_f != min_f else 1
        
        # Valores Y (Distância)
        screen.blit(text_font.render(f"{int(max_f)}k", True, GRAY_L), (panel_x + 5, gy))
        screen.blit(text_font.render(f"{int(min_f)}k", True, GRAY_L), (panel_x + 5, gy + gh - 15))
        
        # Valores X (Gerações)
        screen.blit(text_font.render(f"G:{generation}", True, GRAY_L), (gx + gw - 40, gy + gh + 5))

        # Linha do Gráfico
        pts = [(gx + (i * gw / len(fitness_history)), 
                (gy + gh) - ((f - min_f) / rng * (gh - 10))) 
               for i, f in enumerate(fitness_history)]
        pygame.draw.lines(screen, color_status, False, pts, 2)

    return y_list