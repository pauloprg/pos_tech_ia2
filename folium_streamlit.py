import streamlit as st
import folium
from streamlit_folium import st_folium
import time
import os
from mapa_utils import load_coordinates_from_jsonl, generate_service_points
from genetic_algorithm import generate_random_population, evolve_population

# Centro aproximado de Ceilândia
centro_lat = -15.8219
centro_lon = -48.1072

# Carregar coordenadas do dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSONL_PATH = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
coordinates = load_coordinates_from_jsonl(JSONL_PATH)

# Gerar pontos de atendimento
N_POINTS = 15
POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.20

service_points = generate_service_points(coordinates=coordinates, n_points=N_POINTS)

# Cores por prioridade
priority_colors = {
    1: 'green',
    2: 'blue',
    3: 'orange',
    4: 'red'
}

def create_map(best_route):
    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)

    # Adicionar marcadores para pontos
    for point in service_points:
        folium.Marker(
            location=[point.lat, point.lon],
            popup=f"Ponto {point.id}: {point.tipo_atendimento} (Prioridade {point.prioridade})",
            icon=folium.Icon(color=priority_colors[point.prioridade])
        ).add_to(mapa)

    # Adicionar rota como polyline
    if best_route:
        route_coords = [(point.lat, point.lon) for point in best_route]
        folium.PolyLine(route_coords, color="black", weight=3, opacity=0.8).add_to(mapa)

    return mapa

st.title("Otimização de Rotas em Ceilândia - DF (Tempo Real)")

if 'population' not in st.session_state:
    st.session_state.population = generate_random_population(service_points, POPULATION_SIZE)
    st.session_state.generation = 0
    st.session_state.best_route = st.session_state.population[0][:]
    st.session_state.best_fitness = float("inf")
    st.session_state.running = False

if st.button("Iniciar Otimização"):
    st.session_state.running = True
    st.session_state.generation = 0
    st.session_state.best_route = st.session_state.population[0][:]
    st.session_state.best_fitness = float("inf")

if st.button("Parar"):
    st.session_state.running = False

placeholder = st.empty()

while st.session_state.running:
    st.session_state.generation += 1
    
    st.session_state.population, current_best_route, current_best_fitness = evolve_population(
        population=st.session_state.population,
        population_size=POPULATION_SIZE,
        mutation_probability=MUTATION_PROBABILITY,
        elite_size=1
    )
    
    if current_best_fitness < st.session_state.best_fitness:
        st.session_state.best_fitness = current_best_fitness
        st.session_state.best_route = current_best_route[:]
    
    # Atualizar mapa
    mapa = create_map(st.session_state.best_route)
    
    with placeholder.container():
        st.write(f"Geração: {st.session_state.generation}")
        st.write(f"Melhor Fitness: {round(st.session_state.best_fitness, 2)}")
        st_folium(mapa, width=800, height=600)
    
    time.sleep(0.1)  # Pequena pausa para visualização

if not st.session_state.running:
    mapa = create_map(st.session_state.best_route)
    with placeholder.container():
        st.write(f"Geração Final: {st.session_state.generation}")
        st.write(f"Melhor Fitness: {round(st.session_state.best_fitness, 2)}")
        st_folium(mapa, width=800, height=600)