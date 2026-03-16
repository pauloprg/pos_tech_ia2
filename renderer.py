# -*- coding: utf-8 -*-
import pygame

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE_MAIN = (0, 191, 255)
GOLD = (255, 215, 0)
GRAY_L = (170, 170, 170)

PRIORITY_COLORS = {4: (255, 50, 50), 3: (255, 165, 0), 2: (0, 200, 255), 1: (50, 255, 50)}

def draw_route_lines(screen, route):
    if len(route) < 2: return
    for i in range(len(route) - 1):
        p1, p2 = (route[i].x, route[i].y), (route[i+1].x, route[i+1].y)
        pygame.draw.line(screen, BLUE_MAIN, p1, p2, 4)
        pygame.draw.circle(screen, WHITE, p1, 3)

def draw_service_points(screen, points, font):
    for point in points:
        color = PRIORITY_COLORS.get(point.prioridade, WHITE)
        pygame.draw.circle(screen, color, (point.x, point.y), 9)
        pygame.draw.circle(screen, WHITE, (point.x, point.y), 9, 2)
        lbl = font.render(f"P{point.id}", True, WHITE)
        bg = lbl.get_rect(center=(point.x, point.y - 18))
        pygame.draw.rect(screen, BLACK, bg.inflate(4, 2))
        screen.blit(lbl, bg)

def draw_side_panel(screen, panel_x, panel_width, window_height, title_font, text_font, 
                    route, generation, best_fitness, fitness_history, scroll_offset, is_optimal):
    
    pygame.draw.rect(screen, (30, 30, 30), (panel_x, 0, panel_width, window_height))
    pygame.draw.line(screen, BLUE_MAIN, (panel_x, 0), (panel_x, window_height), 2)

    margin = panel_x + 20
    
    # Rótulo de Status
    status_color = GOLD if is_optimal else BLUE_MAIN
    status_txt = "GERAÇÃO ÓTIMA ATINGIDA" if is_optimal else f"GERAÇÃO: {generation}"
    screen.blit(title_font.render(status_txt, True, status_color), (margin, 20))
    screen.blit(text_font.render(f"Distância Atual: {round(best_fitness, 2)} km", True, WHITE), (margin, 50))

    # Lista Dinâmica
    y_list = 100 - scroll_offset
    for i, p in enumerate(route):
        if 100 < y_list < 580:
            pygame.draw.rect(screen, PRIORITY_COLORS.get(p.prioridade), (margin, y_list + 4, 6, 12))
            screen.blit(text_font.render(f"{i+1}º -> Ponto {p.id} (Prio {p.prioridade})", True, WHITE), (margin + 15, y_list))
        y_list += 22

    # --- GRÁFICO CARTESIANO COM EIXOS X, Y ---
    gx, gy, gw, gh = margin + 40, 620, panel_width - 80, 140
    pygame.draw.line(screen, WHITE, (gx, gy), (gx, gy + gh), 2) # Eixo Y
    pygame.draw.line(screen, WHITE, (gx, gy + gh), (gx + gw, gy + gh), 2) # Eixo X

    if len(fitness_history) > 2:
        max_f, min_f = max(fitness_history), min(fitness_history)
        rng = max_f - min_f if max_f != min_f else 1
        
        # Rótulos Y
        screen.blit(text_font.render(f"{int(max_f)}", True, GRAY_L), (margin, gy))
        screen.blit(text_font.render(f"{int(min_f)}", True, GRAY_L), (margin, gy + gh - 15))
        
        # Rótulos X
        screen.blit(text_font.render(f"G:{max(0, generation-150)}", True, GRAY_L), (gx, gy + gh + 5))
        screen.blit(text_font.render(f"G:{generation}", True, GRAY_L), (gx + gw - 40, gy + gh + 5))

        pts = [(gx + (i * gw / len(fitness_history)), (gy + gh) - ((f - min_f) / rng * (gh - 10))) 
               for i, f in enumerate(fitness_history)]
        pygame.draw.lines(screen, status_color, False, pts, 2)