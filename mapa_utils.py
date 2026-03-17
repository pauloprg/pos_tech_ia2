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

def generate_service_points(
    coords_data=None,
    n_points: int = 15,
    map_width: int = 1000,
    map_height: int = 800,
    *,
    coordinates=None,
    min_dist_px: int = 20,
    max_attempts: int | None = None,
):
    """
    Gera pontos no mapa evitando sobreposição.

    - `coords_data` / `coordinates`: lista de dicts com `lat`, `lon`, `nome_rua`
    - `min_dist_px`: distância mínima (em pixels) entre centros
    - `max_attempts`: limite de tentativas (default: proporcional ao tamanho do dataset)
    """
    if coords_data is None:
        coords_data = coordinates

    if not coords_data or n_points <= 0:
        return []

    # Tentamos preencher com um dataset embaralhado, aceitando só posições que respeitam min_dist_px
    shuffled = list(coords_data)
    random.shuffle(shuffled)

    if max_attempts is None:
        max_attempts = max(500, n_points * 200, len(shuffled))

    min_dist_sq = int(min_dist_px) * int(min_dist_px)
    accepted_pixels: list[tuple[int, int]] = []
    points: list[ServicePoint] = []

    attempts = 0
    idx = 0
    while len(points) < min(n_points, len(shuffled)) and attempts < max_attempts and idx < len(shuffled):
        data = shuffled[idx]
        idx += 1
        attempts += 1

        # Pixels para o Pygame
        x = int((data["lon"] - LON_MIN) / (LON_MAX - LON_MIN) * map_width)
        y = int((LAT_MAX - data["lat"]) / (LAT_MAX - LAT_MIN) * map_height)

        # Garante que o ponto fique dentro do mapa (evita coordenadas limítrofes gerarem fora)
        x = max(0, min(map_width - 1, x))
        y = max(0, min(map_height - 1, y))

        # Verifica distância mínima para evitar sobreposição
        ok = True
        for ax, ay in accepted_pixels:
            dx = x - ax
            dy = y - ay
            if (dx * dx + dy * dy) < min_dist_sq:
                ok = False
                break
        if not ok:
            continue

        accepted_pixels.append((x, y))

        profile = random.choices(
            TIPOS_ATENDIMENTO,
            weights=[item["peso"] for item in TIPOS_ATENDIMENTO],
            k=1,
        )[0]

        points.append(
            ServicePoint(
                id=len(points) + 1,
                x=x,
                y=y,
                lat=data["lat"],
                lon=data["lon"],
                codigo=data.get("nome_rua", "Ceilândia")[:15],
                tipo_atendimento=profile["atendimento"],
                prioridade=profile["prioridade"],
                quantidade=random.randint(*profile["int_qtde"]),
                tempo_inicio=profile["horario"][0],
                tempo_fim=profile["horario"][1],
                tempo_atendimento=round(random.uniform(*profile["tempo_atendimento"]), 2),
                temperatura_controlada=profile["temperatura"],
                protocolo_especial=profile["prot_especial"],
            )
        )

    # Se ainda faltarem pontos (dataset muito denso), relaxa distância gradualmente como fallback
    if len(points) < min(n_points, len(shuffled)):
        remaining = min(n_points, len(shuffled)) - len(points)
        relaxed = max(6, min_dist_px // 2)
        if relaxed < min_dist_px and remaining > 0:
            extra = generate_service_points(
                shuffled[idx:],
                remaining,
                map_width,
                map_height,
                min_dist_px=relaxed,
                max_attempts=max_attempts,
            )
            # Evita duplicar IDs
            for p in extra:
                p.id = len(points) + 1
                points.append(p)

    return points