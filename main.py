# ===== renderer.py (COMPLETO ATUALIZADO) =====
# -*- coding: utf-8 -*-
import pygame
import time

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE_NEON = (0, 191, 255)
GOLD = (255, 215, 0)
GRAY_DARK = (40, 40, 45)
GRAY_LIGHT = (150, 150, 150)

COLOR_USER = (0, 180, 255)
COLOR_AI = (120, 120, 130)
INPUT_BG = (35, 35, 40)
INPUT_BORDER = (0, 255, 150)

PRIORITY_COLORS = {4: (255, 50, 50), 3: (255, 165, 0), 2: (0, 200, 255), 1: (50, 255, 50)}

class BriefingPopup:
    def __init__(self, texto_inicial):
        self.historico_formatado = []
        self.input_usuario = ""
        self.largura, self.altura = 800, 550
        self.visivel = True
        self.carregando = False
        self.scroll_offset = 0
        self.max_linhas_visiveis = 18
        self._scroll_track_rect = None
        self._scroll_thumb_rect = None
        self._scroll_dragging = False
        self._scroll_drag_mouse_y = 0
        self._scroll_drag_start_offset = 0

        self.font_m = pygame.font.SysFont("arial", 16)
        self.font_t = pygame.font.SysFont("arial", 20, bold=True)

        self.adicionar_mensagem("IA", texto_inicial)

    def _max_scroll(self):
        return max(0, len(self.historico_formatado) - self.max_linhas_visiveis)

    def clamp_scroll(self):
        self.scroll_offset = max(0, min(self.scroll_offset, self._max_scroll()))

    def scroll_lines(self, delta_lines):
        # delta_lines > 0 = scroll up (ver mensagens antigas)
        self.scroll_offset = max(0, min(self.scroll_offset + delta_lines, self._max_scroll()))

    def on_mouse_down(self, pos):
        if self._scroll_thumb_rect and self._scroll_thumb_rect.collidepoint(pos):
            self._scroll_dragging = True
            self._scroll_drag_mouse_y = pos[1]
            self._scroll_drag_start_offset = self.scroll_offset
            return True

        if self._scroll_track_rect and self._scroll_track_rect.collidepoint(pos):
            if not self._scroll_thumb_rect:
                return False
            if pos[1] < self._scroll_thumb_rect.top:
                self.scroll_lines(6)  # page up
            elif pos[1] > self._scroll_thumb_rect.bottom:
                self.scroll_lines(-6)  # page down
            return True

        return False

    def on_mouse_up(self):
        self._scroll_dragging = False

    def on_mouse_motion(self, pos):
        if not self._scroll_dragging:
            return False
        if not (self._scroll_track_rect and self._scroll_thumb_rect):
            return False

        max_scroll = self._max_scroll()
        if max_scroll <= 0:
            return True

        track_y = self._scroll_track_rect.y
        track_h = self._scroll_track_rect.height
        thumb_h = self._scroll_thumb_rect.height
        usable_h = max(1, track_h - thumb_h)

        # Determine new thumb top from mouse delta, clamp, then map back to scroll_offset.
        delta_y = pos[1] - self._scroll_drag_mouse_y
        start_fraction = (max_scroll - self._scroll_drag_start_offset) / max_scroll  # 0=top, 1=bottom
        start_thumb_top = track_y + int(usable_h * start_fraction)
        new_thumb_top = max(track_y, min(track_y + usable_h, start_thumb_top + delta_y))
        new_fraction = (new_thumb_top - track_y) / usable_h  # 0=top, 1=bottom
        self.scroll_offset = int(round(max_scroll * (1 - new_fraction)))
        self.clamp_scroll()
        return True

    def adicionar_mensagem(self, autor, texto):
        self.carregando = False
        prefixo = "🤖 Assistente: " if autor == "IA" else "👤 Maitê: "
        cor = COLOR_AI if autor == "IA" else COLOR_USER

        palavras = (prefixo + texto).replace('\n', ' \n ').split(' ')
        linha_atual = ""

        for p in palavras:
            if p == '\n':
                self.historico_formatado.append({"texto": linha_atual, "cor": cor})
                linha_atual = ""
                continue

            test_line = linha_atual + p + " "

            if self.font_m.size(test_line)[0] < (self.largura - 80):
                linha_atual = test_line
            else:
                self.historico_formatado.append({"texto": linha_atual, "cor": cor})
                linha_atual = p + " "

        self.historico_formatado.append({"texto": linha_atual, "cor": cor})
        self.historico_formatado.append({"texto": "", "cor": BLACK})

        self.scroll_offset = 0
        self.clamp_scroll()

    def draw(self, screen):
        if not self.visivel:
            return

        overlay = pygame.Surface((1400, 800), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), (0, 0, 1400, 800))

        x, y = (1000 - self.largura) // 2, (800 - self.altura) // 2
        rect = pygame.Rect(x, y, self.largura, self.altura)

        pygame.draw.rect(overlay, (25, 25, 30), rect, border_radius=15)
        pygame.draw.rect(overlay, BLUE_NEON, rect, 2, border_radius=15)

        overlay.blit(self.font_t.render("✨ Inteligência Logística - IA", True, GOLD), (x+30, y+20))

        self.clamp_scroll()
        message_top = y + 70
        message_bottom = y + self.altura - 80
        message_h = max(1, message_bottom - message_top)
        y_text = message_top

        start = max(0, len(self.historico_formatado) - self.max_linhas_visiveis - self.scroll_offset)
        end = start + self.max_linhas_visiveis

        for item in self.historico_formatado[start:end]:
            if item["texto"]:
                surf = self.font_m.render(item["texto"], True, item["cor"])
                overlay.blit(surf, (x+30, y_text))
            y_text += 22

        # Scrollbar
        total = len(self.historico_formatado)
        max_scroll = self._max_scroll()
        track_w = 10
        track_x = x + self.largura - 18
        track_y = message_top
        track_h = message_h
        track = pygame.Rect(track_x, track_y, track_w, track_h)
        self._scroll_track_rect = track

        if total <= self.max_linhas_visiveis:
            thumb = pygame.Rect(track_x, track_y, track_w, track_h)
        else:
            thumb_h = int(max(24, track_h * (self.max_linhas_visiveis / max(1, total))))
            thumb_h = min(track_h, thumb_h)
            usable_h = max(1, track_h - thumb_h)
            fraction = (max_scroll - self.scroll_offset) / max_scroll  # 0=top, 1=bottom
            thumb_y = track_y + int(usable_h * fraction)
            thumb = pygame.Rect(track_x, thumb_y, track_w, thumb_h)
        self._scroll_thumb_rect = thumb

        pygame.draw.rect(overlay, (55, 55, 65), track, border_radius=5)
        pygame.draw.rect(overlay, (0, 255, 150) if self._scroll_dragging else (120, 120, 130), thumb, border_radius=5)

        if self.carregando:
            loading = self.font_m.render("🤖 Pensando...", True, GOLD)
            overlay.blit(loading, (x+30, y + self.altura - 90))

        input_y = y + self.altura - 60

        pygame.draw.rect(overlay, INPUT_BG, (x+20, input_y, self.largura-40, 40), border_radius=8)
        pygame.draw.rect(overlay, INPUT_BORDER, (x+20, input_y, self.largura-40, 40), 1, border_radius=8)

        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""

        texto_input = self.input_usuario if self.input_usuario else "Digite sua pergunta... (Enter para enviar)"
        txt_input = self.font_m.render(f"{texto_input}{cursor}", True, (0, 255, 150))

        overlay.blit(txt_input, (x+35, input_y + 10))

        screen.blit(overlay, (0, 0))


# ===== main.py (COMPLETO ATUALIZADO) =====
# -*- coding: utf-8 -*-
import sys, pygame, os
from mapa_utils import *
from renderer import *
from genetic_algorithm import *
from ai_advisor import *

WINDOW_WIDTH, WINDOW_HEIGHT = 1400, 800
MAP_WIDTH, PANEL_WIDTH = 1000, 400
FPS = 30

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Saúde da Mulher - Ceilândia")
    clock = pygame.time.Clock()
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, "assets", "dataset_ceilandia_osm.jsonl")
    
    coords_data = load_coordinates_from_jsonl(json_path)
    service_points = generate_service_points(coords_data, 15, MAP_WIDTH, WINDOW_HEIGHT)
    
    population = generate_random_population(service_points, 100)
    best_fitness = float("inf")
    fitness_history = []
    generation, stable_count, is_optimal = 0, 0, False
    popup = None
    best_route = []

    try:
        map_surface = load_and_scale_map(os.path.join(BASE_DIR, "mapa_vibrante.png"), MAP_WIDTH, WINDOW_HEIGHT)
    except:
        map_surface = None

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if popup and popup.visivel:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Mouse wheel (pygame 1) and drag/click on scrollbar
                    if event.button == 4:
                        popup.scroll_lines(3)
                        continue
                    if event.button == 5:
                        popup.scroll_lines(-3)
                        continue
                    if event.button == 1:
                        if popup.on_mouse_down(mouse_pos):
                            continue

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        popup.on_mouse_up()

                if event.type == pygame.MOUSEMOTION:
                    if popup.on_mouse_motion(mouse_pos):
                        continue

                if event.type == pygame.MOUSEWHEEL:
                    # pygame 2 (trackpad / wheel)
                    if event.y != 0:
                        popup.scroll_lines(3 if event.y > 0 else -3)
                        continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        popup.visivel = False

                    elif event.key == pygame.K_RETURN:
                        if popup.input_usuario.strip():
                            msg = popup.input_usuario
                            popup.input_usuario = ""
                            popup.carregando = True
                            popup.draw(screen); pygame.display.flip()

                            res = enviar_mensagem_chat(msg)

                            popup.adicionar_mensagem("Gerreiro", msg)
                            popup.adicionar_mensagem("IA", res)

                    elif event.key == pygame.K_BACKSPACE:
                        popup.input_usuario = popup.input_usuario[:-1]

                    elif event.key == pygame.K_UP:
                        popup.scroll_lines(3)

                    elif event.key == pygame.K_DOWN:
                        popup.scroll_lines(-3)

                    elif event.key == pygame.K_DELETE:
                        popup.historico_formatado = []
                        popup.scroll_offset = 0

                    elif event.key == pygame.K_TAB:
                        popup.input_usuario += "    "

                    else:
                        popup.input_usuario += event.unicode
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                btn_rect = pygame.Rect(MAP_WIDTH + 50, 530, 300, 45)
                if btn_rect.collidepoint(mouse_pos) and is_optimal:
                    if not popup:
                        briefing = gerar_roteiro_inteligente(best_route)
                        inicializar_chat(best_route)
                        popup = BriefingPopup(briefing)
                    else:
                        popup.visivel = True

        if not is_optimal:
            generation += 1
            population, cur_best, cur_fit = evolve_population(population, 100, 0.25)
            if cur_fit < best_fitness:
                best_fitness, best_route, stable_count = cur_fit, cur_best[:], 0
            else:
                stable_count += 1
            if stable_count > 500:
                is_optimal = True
            fitness_history.append(best_fitness)
            if len(fitness_history) > 150:
                fitness_history.pop(0)

        screen.fill(BLACK)
        if map_surface:
            screen.blit(map_surface, (0, 0))

        draw_route_lines(screen, best_route)
        draw_service_points(screen, best_route if best_route else service_points, pygame.font.SysFont("arial", 11))

        best_distance_km = calculate_total_distance_km(best_route) if best_route else 0.0

        draw_side_panel(screen, MAP_WIDTH, PANEL_WIDTH, WINDOW_HEIGHT,
                        pygame.font.SysFont("arial", 18, True), pygame.font.SysFont("arial", 13),
                        best_route, generation, best_fitness, best_distance_km, fitness_history, 0, is_optimal)

        draw_chat_button(screen, MAP_WIDTH + 50, 530, 300, 45, is_optimal)

        if popup and popup.visivel:
            popup.draw(screen)

        draw_convergence_graph(screen, MAP_WIDTH + 30, 600, PANEL_WIDTH - 60, 160, fitness_history)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
