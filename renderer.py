# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:54:21 2026

@author: paulo.goncalves
"""
import pygame
from pontos import ServicePoint


WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (220, 220, 220)
RED = (220, 50, 50)
ORANGE = (255, 140, 0)
BLUE = (50, 90, 220)
GREEN = (40, 170, 90)
PURPLE = (140, 70, 180)


def get_priority_color(priority: int) -> tuple[int, int, int]:
    if priority == 4:
        return RED
    if priority == 3:
        return ORANGE
    if priority == 2:
        return BLUE
    return GREEN


def draw_route_lines(screen: pygame.Surface, points: list[ServicePoint]) -> None:
    if len(points) < 2:
        return

    for i in range(len(points) - 1):
        start = points[i].posicao()
        end = points[i + 1].posicao()
        pygame.draw.line(screen, PURPLE, start, end, 2)


def draw_service_points(screen: pygame.Surface, points: list[ServicePoint], font: pygame.font.Font) -> None:
    for point in points:
        color = get_priority_color(point.prioridade)
        pygame.draw.circle(screen, color, point.posicao(), 7)
        label = font.render(str(point.id), True, BLACK)
        screen.blit(label, (point.x + 8, point.y - 8))


def draw_colored_bullet(
    screen: pygame.Surface,
    x: int,
    y: int,
    color: tuple[int, int, int],
    radius: int = 5
) -> None:
    pygame.draw.circle(screen, color, (x, y), radius)


def draw_side_panel(
    screen: pygame.Surface,
    panel_x: int,
    panel_width: int,
    window_height: int,
    title_font: pygame.font.Font,
    text_font: pygame.font.Font,
    route: list[ServicePoint]
) -> None:
    pygame.draw.rect(screen, GRAY, (panel_x, 0, panel_width, window_height))

    title = title_font.render("Rota em tempo real", True, BLACK)
    screen.blit(title, (panel_x + 16, 16))

    # LEGENDA COM CORES
    LEGENDAS = [
        (4, "4 = Emergência obstétrica"),
        (3, "3 = Violência doméstica"),
        (2, "2 = Medicamento hormonal"),
        (1, "1 = Pós-parto"),
    ]

    legend_title = text_font.render("Prioridades:", True, BLACK)
    screen.blit(legend_title, (panel_x + 16, 52))

    y = 78
    for prioridade, text_line in LEGENDAS:
        color = get_priority_color(prioridade)

        # bolinha colorida
        draw_colored_bullet(screen, panel_x + 22, y + 7, color, radius=5)

        # texto da legenda
        text_surface = text_font.render(text_line, True, BLACK)
        screen.blit(text_surface, (panel_x + 36, y))

        y += 22

    y += 10

    TIPOS_ATENDIMENTOS = {
        "Emergência obstétrica": "Emergência obstétrica",
        "Violência doméstica": "Violência doméstica",
        "Medicamento hormonal": "Medicamento hormonal",
        "Pós-parto": "Pós-parto",
    }

    # LISTA DA ROTA COM BOLINHA DA MESMA COR DO MAPA
    for idx, point in enumerate(route, start=1):
        tipo = TIPOS_ATENDIMENTOS.get(point.tipo_atendimento, point.tipo_atendimento)
        color = get_priority_color(point.prioridade)

        # bolinha colorida ao lado do item da rota
        draw_colored_bullet(screen, panel_x + 22, y + 7, color, radius=5)

        line = (
            f"{idx}. P{point.id} | "
            f"{tipo} | {point.tempo_inicio}-{point.tempo_fim}h"
        )

        line_surface = text_font.render(line, True, BLACK)
        screen.blit(line_surface, (panel_x + 36, y))
        y += 18