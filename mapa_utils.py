# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:50:42 2026

@author: paulo.goncalves
"""

import random
import pygame
from pontos import ServicePoint

TIPOS_ATENDIMENTO = [
    {
        "atendimento": "Emergência obstétrica",
        "prioridade": 4,
        "int_qtde": (2, 5),
        "horario": (0, 23),
        "tempo_atendimento": (0.8, 1.5),
        "temperatura": False,
        "prot_especial": False,
        "peso": 20
    },
    {
        "atendimento": "Violência doméstica",
        "prioridade": 3,
        "int_qtde": (1, 3),
        "horario": (6, 20),
        "tempo_atendimento": (0.8, 1.3),
        "temperatura": False,
        "prot_especial": True,
        "peso": 15
    },
    {
        "atendimento": "Medicamento hormonal",
        "prioridade": 2,
        "int_qtde": (1, 4),
        "horario": (8, 18),
        "tempo_atendimento": (0.2, 0.5),
        "temperatura": True,
        "prot_especial": False,
        "peso": 30
    },
    {
        "atendimento": "Pós-parto",
        "prioridade": 1,
        "int_qtde": (1, 2),
        "horario": (9, 17),
        "tempo_atendimento": (0.5, 1.0),
        "temperatura": False,
        "prot_especial": False,
        "peso": 35
    }
]


def load_and_scale_map(image_path: str, map_width: int, map_height: int) -> pygame.Surface:
    image = pygame.image.load(image_path)
    image = pygame.transform.smoothscale(image, (map_width, map_height))
    return image


def is_blackish(rgb: tuple[int, int, int], threshold: int = 25) -> bool:
    r, g, b = rgb
    return r < threshold and g < threshold and b < threshold

def is_bluish_water(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return b > 150 and g > 120 and r < 120


def build_valid_positions(map_surface: pygame.Surface) -> list[tuple[int, int]]:
    valid_positions = []

    width = map_surface.get_width()
    height = map_surface.get_height()

    for x in range(width):
        for y in range(height):
            color = map_surface.get_at((x, y))
            rgb = (color.r, color.g, color.b)

            if not is_blackish(rgb) and not is_bluish_water(rgb):
                valid_positions.append((x, y))

    return valid_positions


def synthetic_patient_code(index: int) -> str:
    return f"PAC-{index:03d}"


def generate_synthetic_service_point(point_id: int, x: int, y: int) -> ServicePoint:
    profile = random.choices(
        TIPOS_ATENDIMENTO,
        weights=[item["peso"] for item in TIPOS_ATENDIMENTO],
        k=1
    )[0]

    demanda = random.randint(*profile["int_qtde"])
    hora_inicio, hora_fim = profile["horario"]
    tempo_atend = round(random.uniform(*profile["tempo_atendimento"]), 2)

    return ServicePoint(
        id=point_id,
        x=x,
        y=y,
        codigo=synthetic_patient_code(point_id),
        tipo_atendimento=profile["atendimento"],
        prioridade=profile["prioridade"],
        quantidade=demanda,
        tempo_inicio=hora_inicio,
        tempo_fim=hora_fim,
        tempo_atendimento=tempo_atend,
        temperatura_controlada=profile["temperatura"],
        protocolo_especial=profile["prot_especial"]
    )


def generate_service_points(
    valid_positions: list[tuple[int, int]],
    n_points: int
) -> list[ServicePoint]:
    selected_positions = random.sample(valid_positions, n_points)
    points = []

    for i, (x, y) in enumerate(selected_positions, start=1):
        point = generate_synthetic_service_point(i, x, y)
        points.append(point)

    return points