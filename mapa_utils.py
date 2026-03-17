# -*- coding: utf-8 -*-
import random
import pygame
import json
import os
from pontos import ServicePoint

# NOVOS LIMITES (ZOOM OUT) - Abrangendo mais áreas ao redor de Ceilândia
LAT_MAX = -15.7000  # Subiu um pouco (mais ao norte)
LAT_MIN = -15.9500  # Desceu um pouco (mais ao sul)
LON_MIN = -48.2500  # Abriu para a esquerda (oeste)
LON_MAX = -47.9500  # Abriu para a direita (leste - rumo ao Plano Piloto)

TIPOS_ATENDIMENTO = [
    {"atendimento": "Emergência obstétrica", "prioridade": 4, "int_qtde": (1, 1), "horario": (0, 23), "tempo_atendimento": (0.8, 1.5), "temperatura": False, "prot_especial": False, "peso": 20},
    {"atendimento": "Violência doméstica", "prioridade": 3, "int_qtde": (1, 1), "horario": (6, 20), "tempo_atendimento": (0.8, 1.3), "temperatura": False, "prot_especial": True, "peso": 15},
    {"atendimento": "Medicamento hormonal", "prioridade": 2, "int_qtde": (1, 4), "horario": (8, 18), "tempo_atendimento": (0.2, 0.5), "temperatura": True, "prot_especial": False, "peso": 30},
    {"atendimento": "Pós-parto", "prioridade": 1, "int_qtde": (1, 2), "horario": (9, 17), "tempo_atendimento": (0.5, 1.0), "temperatura": False, "prot_especial": False, "peso": 35}
]

def load_and_scale_map(image_path: str, map_width: int, map_height: int) -> pygame.Surface:
    image = pygame.image.load(image_path)
    return pygame.transform.smoothscale(image, (map_width, map_height))

def load_coordinates_from_jsonl(file_path):
    """Extrai lat/lon das linhas que contém coordenadas no campo input ou output."""
    coords = []
    if not os.path.exists(file_path):
        return coords

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                # Verifica se a instrução pede endereço (onde o input é a coordenada)
                # Exemplo: "input": "-15.802493, -48.118458"
                texto_alvo = data.get("input", "")
                if "," in texto_alvo and texto_alvo.split(",")[0].strip().startswith("-15"):
                    partes = texto_alvo.split(",")
                    lat = float(partes[0].strip())
                    lon = float(partes[1].strip())
                    rua = data.get("output", "Ceilândia")
                    coords.append({"lat": lat, "lon": lon, "nome_rua": rua})
            except:
                continue
    return coords

def generate_service_points(coords_data, n_points, map_width, map_height):
    if not coords_data:
        return []

    selected = random.sample(coords_data, min(n_points, len(coords_data)))
    points = []

    for i, data in enumerate(selected, start=1):
        # Pixels para o Pygame
        x = int((data['lon'] - LON_MIN) / (LON_MAX - LON_MIN) * map_width)
        y = int((LAT_MAX - data['lat']) / (LAT_MAX - LAT_MIN) * map_height)
        
        profile = random.choices(
            TIPOS_ATENDIMENTO,
            weights=[item["peso"] for item in TIPOS_ATENDIMENTO],
            k=1
        )[0]

        # Agora passamos lat e lon explicitamente para o construtor
        points.append(ServicePoint(
            id=i, 
            x=x, 
            y=y,
            lat=data['lat'], # <--- PASSANDO LATITUDE REAL
            lon=data['lon'], # <--- PASSANDO LONGITUDE REAL
            #data['nome_rua'] somente os 15 primeiros caracteres para evitar textos longos
            codigo=data['nome_rua'][:15],
            tipo_atendimento=profile["atendimento"],
            prioridade=profile["prioridade"],
            quantidade=random.randint(*profile["int_qtde"]),
            tempo_inicio=profile["horario"][0],
            tempo_fim=profile["horario"][1],
            tempo_atendimento=round(random.uniform(*profile["tempo_atendimento"]), 2),
            temperatura_controlada=profile["temperatura"],
            protocolo_especial=profile["prot_especial"]
        ))
    return points