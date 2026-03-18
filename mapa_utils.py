# -*- coding: utf-8 -*-
import random
import pygame
import json
import os
from pontos import Depot, ServicePoint, Vehicle


# NOVOS LIMITES (ZOOM OUT) - Abrangendo mais áreas ao redor de Ceilândia
LAT_MAX = -15.7000  # mais ao norte
LAT_MIN = -15.9500  # mais ao sul
LON_MIN = -48.2500  # mais a oeste
LON_MAX = -47.9500  # mais a leste

TIPOS_ATENDIMENTO = [
    {
        "atendimento": "Emergência obstétrica",
        "prioridade": 4,
        "int_qtde": (1, 1),
        "horario": (0, 23),
        "tempo_atendimento": (0.8, 1.5),
        "temperatura": False,
        "prot_especial": False,
        "peso": 20
    },
    {
        "atendimento": "Violência doméstica",
        "prioridade": 3,
        "int_qtde": (1, 1),
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


def build_default_depot(map_width: int, map_height: int) -> Depot:
    return Depot(
        x=map_width // 2,
        y=map_height // 2,
        lat=-15.8150,
        lon=-48.1000,
        nome="Base Saúde da Mulher DF"
    )


def build_default_fleet() -> list[Vehicle]:
    return [
        Vehicle(
            id=1,
            nome="Moto 01",
            tipo="moto",
            velocidade_kmh=55.0,
            custo_km=1.2,
            capacidade_suprimentos=12,
            max_paradas=8,
            max_distancia_km=90.0,
            tipos_atendimento={
                "Emergência obstétrica",
                "Violência doméstica",
                "Pós-parto",
            },
            suporta_temperatura_controlada=False,
            suporta_protocolo_especial=True,
        ),
        Vehicle(
            id=2,
            nome="Van Refrigerada 01",
            tipo="van_refrigerada",
            velocidade_kmh=40.0,
            custo_km=2.5,
            capacidade_suprimentos=40,
            max_paradas=14,
            max_distancia_km=160.0,
            tipos_atendimento={
                "Medicamento hormonal",
                "Pós-parto",
                "Violência doméstica",
            },
            suporta_temperatura_controlada=True,
            suporta_protocolo_especial=True,
        ),
        Vehicle(
            id=3,
            nome="Ambulância 01",
            tipo="ambulancia",
            velocidade_kmh=60.0,
            custo_km=3.8,
            capacidade_suprimentos=18,
            max_paradas=6,
            max_distancia_km=140.0,
            tipos_atendimento={
                "Emergência obstétrica",
                "Violência doméstica",
            },
            suporta_temperatura_controlada=False,
            suporta_protocolo_especial=True,
        ),
        Vehicle(
            id=4,
            nome="Drone 01",
            tipo="drone",
            velocidade_kmh=70.0,
            custo_km=0.9,
            capacidade_suprimentos=4,
            max_paradas=4,
            max_distancia_km=35.0,
            tipos_atendimento={
                "Medicamento hormonal",
            },
            suporta_temperatura_controlada=True,
            suporta_protocolo_especial=False,
        ),
    ]


def tipos_permitidos_por_atendimento(tipo_atendimento: str) -> set[str]:
    mapa = {
        "Emergência obstétrica": {"ambulancia", "moto"},
        "Violência doméstica": {"ambulancia", "moto", "van_refrigerada"},
        "Medicamento hormonal": {"van_refrigerada", "drone"},
        "Pós-parto": {"moto", "van_refrigerada"},
    }
    return mapa.get(tipo_atendimento, set())


def load_and_scale_map(image_path: str, map_width: int, map_height: int) -> pygame.Surface:
    image = pygame.image.load(image_path)
    return pygame.transform.smoothscale(image, (map_width, map_height))


def load_coordinates_from_jsonl(file_path):
    """Extrai lat/lon das linhas que contêm coordenadas no campo input."""
    coords = []
    if not os.path.exists(file_path):
        return coords

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                texto_alvo = data.get("input", "")
                if "," in texto_alvo and texto_alvo.split(",")[0].strip().startswith("-15"):
                    partes = texto_alvo.split(",")
                    lat = float(partes[0].strip())
                    lon = float(partes[1].strip())
                    rua = data.get("output", "Ceilândia")
                    coords.append({"lat": lat, "lon": lon, "nome_rua": rua})
            except Exception:
                continue
    return coords


def _criar_service_point(data, x, y, point_id):
    profile = random.choices(
        TIPOS_ATENDIMENTO,
        weights=[item["peso"] for item in TIPOS_ATENDIMENTO],
        k=1,
    )[0]

    return ServicePoint(
        id=point_id,
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
        tipos_veiculo_permitidos=tipos_permitidos_por_atendimento(profile["atendimento"]),
    )


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
    Gera pontos no mapa.

    - `coords_data` / `coordinates`: lista de dicts com `lat`, `lon`, `nome_rua`
    - `min_dist_px`: distância mínima (em pixels) entre centros
    - `max_attempts`: limite de tentativas
    """
    if coords_data is None:
        coords_data = coordinates

    if not coords_data or n_points <= 0:
        return []

    shuffled = list(coords_data)
    random.shuffle(shuffled)

    if max_attempts is None:
        max_attempts = max(500, n_points * 200, len(shuffled))

    min_dist_sq = int(min_dist_px) * int(min_dist_px)
    accepted_pixels: list[tuple[int, int]] = []
    points: list[ServicePoint] = []

    attempts = 0
    idx = 0
    target_points = min(n_points, len(shuffled))

    while len(points) < target_points and attempts < max_attempts and idx < len(shuffled):
        data = shuffled[idx]
        idx += 1
        attempts += 1

        x = int((data["lon"] - LON_MIN) / (LON_MAX - LON_MIN) * map_width)
        y = int((LAT_MAX - data["lat"]) / (LAT_MAX - LAT_MIN) * map_height)

        x = max(0, min(map_width - 1, x))
        y = max(0, min(map_height - 1, y))

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
        points.append(_criar_service_point(data, x, y, len(points) + 1))

    # fallback: relaxa a distância mínima gradualmente
    if len(points) < target_points:
        remaining = target_points - len(points)
        relaxed = max(6, min_dist_px // 2)

        if relaxed < min_dist_px and remaining > 0:
            extra = generate_service_points(
                coords_data=shuffled[idx:],
                n_points=remaining,
                map_width=map_width,
                map_height=map_height,
                min_dist_px=relaxed,
                max_attempts=max_attempts,
            )

            for p in extra:
                novo_ponto = ServicePoint(
                    id=len(points) + 1,
                    x=p.x,
                    y=p.y,
                    lat=p.lat,
                    lon=p.lon,
                    codigo=p.codigo,
                    tipo_atendimento=p.tipo_atendimento,
                    prioridade=p.prioridade,
                    quantidade=p.quantidade,
                    tempo_inicio=p.tempo_inicio,
                    tempo_fim=p.tempo_fim,
                    tempo_atendimento=p.tempo_atendimento,
                    temperatura_controlada=p.temperatura_controlada,
                    protocolo_especial=p.protocolo_especial,
                    tipos_veiculo_permitidos=p.tipos_veiculo_permitidos,
                )
                points.append(novo_ponto)

    return points