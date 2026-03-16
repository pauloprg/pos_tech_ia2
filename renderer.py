# -*- coding: utf-8 -*-
import pygame
from pontos import ServicePoint
from typing import List

# Cores do Sistema
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (200, 200, 200)
BLUE_ROUTE = (0, 102, 204)
PANEL_BG = (245, 245, 245)

# Cores de Prioridade (Padrão do Projeto)
PRIORITY_COLORS = {
    4: (255, 0, 0),    # Vermelho - Emergência
    3: (255, 128, 0),  # Laranja - Violência
    2: (0, 128, 255),  # Azul - Medicamento
    1: (0, 153, 76)    # Verde - Pós-parto
}

def draw_route_lines(screen: pygame.Surface, route: List[ServicePoint]):
    """Desenha as linhas conectando os pontos na ordem da melhor rota."""
    if len(route) < 2:
        return

    # Desenha as linhas entre os pontos
    for i in range(len(route) - 1):
        start_pos = (route[i].x, route[i].y)
        end_pos = (route[i+1].x, route[i+1].y)
        
        # Linha principal
        pygame.draw.line(screen, BLUE_ROUTE, start_pos, end_pos, 3)
        
        # Pequena seta ou círculo para indicar direção pode ser adicionado aqui
        pygame.draw.circle(screen, BLUE_ROUTE, start_pos, 4)

def draw_service_points(screen: pygame.Surface, points: List[ServicePoint], font: pygame.font.Font):
    """Desenha os círculos dos pontos de atendimento no mapa."""
    for point in points:
        color = PRIORITY_COLORS.get(point.prioridade, GRAY)
        pos = (point.x, point.y)
        
        # Sombra/Borda para destaque
        pygame.draw.circle(screen, BLACK, pos, 9)
        # Círculo principal
        pygame.draw.circle(screen, color, pos, 7)
        
        # ID do ponto acima dele
        label = font.render(f"P{point.id}", True, BLACK)
        screen.blit(label, (point.x + 8, point.y - 12))

def draw_side_panel(screen, panel_x, panel_width, window_height, title_font, text_font, 
                    route, generation, best_fitness, fitness_history, scroll_offset):
    """Renderiza o painel lateral com informações da rota e evolução."""
    
    # 1. Fundo do Painel
    panel_rect = pygame.Rect(panel_x, 0, panel_width, window_height)
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, GRAY, (panel_x, 0), (panel_x, window_height), 2)

    y_offset = 20 - scroll_offset
    margin = panel_x + 20

    # 2. Cabeçalho de Status
    title = title_font.render(f"Geração: {generation}", True, BLACK)
    screen.blit(title, (margin, y_offset))
    y_offset += 30
    
    fit_text = text_font.render(f"Melhor Fitness: {round(best_fitness, 2)} km", True, BLUE_ROUTE)
    screen.blit(fit_text, (margin, y_offset))
    y_offset += 40

    # 3. Lista da Rota (Sequência de Atendimento)
    header_route = title_font.render("Sequência de Atendimento:", True, BLACK)
    screen.blit(header_route, (margin, y_offset))
    y_offset += 35

    for i, point in enumerate(route):
        if y_offset > -20 and y_offset < window_height:
            # Indicador de ordem
            color = PRIORITY_COLORS.get(point.prioridade, GRAY)
            pygame.draw.rect(screen, color, (margin, y_offset, 5, 15))
            
            info = f"{i+1}º - [P{point.id}] {point.tipo_atendimento} (Prio {point.prioridade})"
            txt = text_font.render(info, True, BLACK)
            screen.blit(txt, (margin + 15, y_offset))
        
        y_offset += 22

    # 4. Desenho do Gráfico de Fitness (Simples)
    y_offset += 20
    if len(fitness_history) > 2:
        graph_header = title_font.render("Evolução (Fitness):", True, BLACK)
        screen.blit(graph_header, (margin, y_offset))
        y_offset += 30
        
        # Área do gráfico
        graph_height = 80
        graph_width = panel_width - 60
        pygame.draw.rect(screen, WHITE, (margin, y_offset, graph_width, graph_height))
        
        if max(fitness_history) != min(fitness_history):
            points_list = []
            for i, val in enumerate(fitness_history):
                px = margin + (i * (graph_width / len(fitness_history)))
                # Inverte para o gráfico subir quando o fitness diminui
                norm_val = (val - min(fitness_history)) / (max(fitness_history) - min(fitness_history))
                py = y_offset + graph_height - (norm_val * graph_height)
                points_list.append((px, py))
            
            if len(points_list) > 1:
                pygame.draw.lines(screen, BLUE_ROUTE, False, points_list, 2)

    # Retorna o y_offset total para controle de scroll no main.py
    return max(0, y_offset + 50 - window_height + scroll_offset)