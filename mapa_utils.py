# -*- coding: utf-8 -*-
import random
import pygame
import json
import os
from pontos import ServicePoint

# Definição dos limites geográficos da Ceilândia
LAT_MIN, LAT_MAX = -15.8600, -15.7900
LON_MIN, LON_MAX = -48.1400, -48.0700

def load_and_scale_map(map_path, width, height):
    """Carrega a imagem do mapa e redimensiona para o Pygame."""
    try:
        if os.path.exists(map_path):
            map_surface = pygame.image.load(map_path)
            return pygame.transform.scale(map_surface, (width, height))
        else:
            fallback = pygame.Surface((width, height))
            fallback.fill((200, 200, 200))
            return fallback
    except Exception as e:
        print(f"Erro ao carregar mapa: {e}")
        return pygame.Surface((width, height))

def latlon_to_pixel(lat, lon, map_width, map_height):
    """Converte coordenadas geográficas para pixels."""
    x = int((lon - LON_MIN) / (LON_MAX - LON_MIN) * map_width)
    y = int((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * map_height)
    return x, y

def load_coordinates_from_jsonl(file_path):
    """Carrega coordenadas reais do arquivo JSONL."""
    coordinates = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if LAT_MIN <= data['lat'] <= LAT_MAX and LON_MIN <= data['lon'] <= LON_MAX:
                        coordinates.append((data['lat'], data['lon']))
                except:
                    continue
    return coordinates

def generate_service_points(coordinates=None, n_points=15, map_width=1000, map_height=800):
    """Gera 15 pontos concentrados no centro da Ceilândia."""
    service_points = []
    
    # Centro aproximado da Ceilândia
    LAT_CENTER, LON_CENTER = -15.8219, -48.1072
    # Margem menor para concentrar os pontos (aproximadamente 3-4km de raio)
    OFFSET = 0.015 

    tipos = [
        ("Emergência obstétrica", 4, True, True),
        ("Violência doméstica", 3, False, True),
        ("Medicamento hormonal", 2, True, False),
        ("Atendimento pós-parto", 1, False, False)
    ]

    for i in range(n_points):
        # Se houver coordenadas reais, tenta pegar as que estão mais próximas do centro
        if coordinates and len(coordinates) > 0:
            # Filtra coordenadas que estão dentro da margem central
            central_coords = [c for c in coordinates if abs(c[0] - LAT_CENTER) < OFFSET and abs(c[1] - LON_CENTER) < OFFSET]
            if central_coords:
                lat, lon = random.choice(central_coords)
            else:
                lat, lon = random.choice(coordinates)
        else:
            # Sorteio puramente aleatório restrito ao centro
            lat = random.uniform(LAT_CENTER - OFFSET, LAT_CENTER + OFFSET)
            lon = random.uniform(LON_CENTER - OFFSET, LON_CENTER + OFFSET)

        # Conversão para pixels usando os limites globais para manter a proporção no mapa
        x, y = latlon_to_pixel(lat, lon, map_width, map_height)
        
        # Garante que os pontos fiquem visíveis dentro da área do mapa no Pygame
        x = max(50, min(x, map_width - 50))
        y = max(50, min(y, map_height - 50))

        tipo_nome, prioridade, temp_ctrl, prot_esp = random.choice(tipos)

        point = ServicePoint(
            id=i + 1, lat=lat, lon=lon, x=x, y=y,
            codigo=f"CEI-{1000 + i}", tipo_atendimento=tipo_nome,
            prioridade=prioridade, quantidade=random.randint(1, 5),
            tempo_inicio=8, tempo_fim=18, tempo_atendimento=1.0,
            temperatura_controlada=temp_ctrl, protocolo_especial=prot_esp
        )
        service_points.append(point)
    return service_points