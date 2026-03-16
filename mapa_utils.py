# -*- coding: utf-8 -*-
import random, pygame, json, os
from pontos import ServicePoint

LAT_MIN, LAT_MAX = -15.8600, -15.7900
LON_MIN, LON_MAX = -48.1400, -48.0700

def load_and_scale_map(map_path, width, height):
    if os.path.exists(map_path):
        return pygame.transform.scale(pygame.image.load(map_path), (width, height))
    return None

def latlon_to_pixel(lat, lon, w, h):
    x = int((lon - LON_MIN) / (LON_MAX - LON_MIN) * w)
    y = int((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * h)
    return x, y

def load_coordinates_from_jsonl(path):
    coords = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    d = json.loads(line)
                    coords.append((d['lat'], d['lon']))
                except: continue
    return coords

def generate_service_points(coordinates, n_points, w, h):
    # Centro da Ceilândia para concentrar os pontos
    C_LAT, C_LON, OFFSET = -15.8219, -48.1072, 0.015
    service_points = []
    tipos = [("Emergência", 4), ("Violência", 3), ("Medicamento", 2), ("Pós-parto", 1)]

    for i in range(n_points):
        lat = random.uniform(C_LAT - OFFSET, C_LAT + OFFSET)
        lon = random.uniform(C_LON - OFFSET, C_LON + OFFSET)
        x, y = latlon_to_pixel(lat, lon, w, h)
        t_nome, prio = random.choice(tipos)
        service_points.append(ServicePoint(i+1, lat, lon, x, y, f"C-{i}", t_nome, prio, 1, 8, 18, 1.0, False, False))
    return service_points