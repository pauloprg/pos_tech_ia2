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

PRIORITY_COLORS = {
    4: (255, 50, 50),
    3: (255, 165, 0),
    2: (0, 200, 255),
    1: (50, 255, 50)
}


class BriefingPopup:
    def __init__(self, texto_inicial):
        self.historico_formatado = []
        self.input_usuario = ""
        self.largura, self.altura = 800, 550
        self.visivel = True
        self.carregando = False

        # scroll_offset = quantas linhas acima do fundo estamos vendo
        # 0 = grudado no final (mensagens mais recentes)
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
        # delta_lines > 0 = sobe no histórico
        # delta_lines < 0 = desce para mensagens mais recentes
        self.scroll_offset += delta_lines
        self.clamp_scroll()

    def handle_event(self, event):
        if not self.visivel:
            return False

        popup_rect = self._get_popup_rect()

        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if popup_rect.collidepoint(mouse_pos):
                # No pygame, y > 0 = roda para cima
                self.scroll_lines(event.y * 3)
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not popup_rect.collidepoint(event.pos):
                return False

            # Compatibilidade com eventos antigos do mouse wheel
            if event.button == 4:
                self.scroll_lines(3)
                return True
            elif event.button == 5:
                self.scroll_lines(-3)
                return True
            elif event.button == 1:
                return self.on_mouse_down(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.on_mouse_up()
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self._scroll_dragging:
                return self.on_mouse_motion(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                self.scroll_lines(8)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_lines(-8)
                return True
            elif event.key == pygame.K_UP:
                self.scroll_lines(1)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_lines(-1)
                return True

        return False

    def _get_popup_rect(self):
        screen_w, screen_h = 1400, 800
        x = (screen_w - self.largura) // 2
        y = (screen_h - self.altura) // 2
        return pygame.Rect(x, y, self.largura, self.altura)

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
                self.scroll_lines(6)   # sobe no histórico
            elif pos[1] > self._scroll_thumb_rect.bottom:
                self.scroll_lines(-6)  # desce para mais recente
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

        delta_y = pos[1] - self._scroll_drag_mouse_y

        # Quando scroll_offset = 0, thumb fica embaixo
        # Quando scroll_offset = max_scroll, thumb fica em cima
        start_fraction = self._scroll_drag_start_offset / max_scroll
        start_thumb_top = track_y + int((1 - start_fraction) * usable_h)

        new_thumb_top = start_thumb_top + delta_y
        new_thumb_top = max(track_y, min(track_y + usable_h, new_thumb_top))

        new_fraction_from_top = (new_thumb_top - track_y) / usable_h
        new_offset = int(round((1 - new_fraction_from_top) * max_scroll))

        self.scroll_offset = new_offset
        self.clamp_scroll()
        return True

    def adicionar_mensagem(self, autor, texto):
        self.carregando = False
        prefixo = "🤖 Assistente: " if autor == "IA" else "👤 Usuário: "
        cor = COLOR_AI if autor == "IA" else COLOR_USER

        palavras = (prefixo + texto).replace('\n', ' \n ').split(' ')
        linha_atual = ""

        for p in palavras:
            if p == '\n':
                self.historico_formatado.append({"texto": linha_atual.rstrip(), "cor": cor})
                linha_atual = ""
                continue

            test_line = linha_atual + p + " "

            if self.font_m.size(test_line)[0] < (self.largura - 95):
                linha_atual = test_line
            else:
                self.historico_formatado.append({"texto": linha_atual.rstrip(), "cor": cor})
                linha_atual = p + " "

        if linha_atual.strip():
            self.historico_formatado.append({"texto": linha_atual.rstrip(), "cor": cor})

        self.historico_formatado.append({"texto": "", "cor": BLACK})

        # ao chegar mensagem nova, volta para o final
        self.scroll_offset = 0
        self.clamp_scroll()

    def draw(self, screen):
        if not self.visivel:
            return

        screen_w, screen_h = screen.get_size()

        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), (0, 0, screen_w, screen_h))

        x, y = (screen_w - self.largura) // 2, (screen_h - self.altura) // 2
        rect = pygame.Rect(x, y, self.largura, self.altura)

        pygame.draw.rect(overlay, (25, 25, 30), rect, border_radius=15)
        pygame.draw.rect(overlay, BLUE_NEON, rect, 2, border_radius=15)

        overlay.blit(self.font_t.render("✨ Inteligência Logística - IA", True, GOLD), (x + 30, y + 20))

        self.clamp_scroll()

        message_top = y + 70
        message_bottom = y + self.altura - 80
        message_h = max(1, message_bottom - message_top)
        y_text = message_top

        total = len(self.historico_formatado)
        start = max(0, total - self.max_linhas_visiveis - self.scroll_offset)
        end = min(total, start + self.max_linhas_visiveis)

        for item in self.historico_formatado[start:end]:
            if item["texto"]:
                surf = self.font_m.render(item["texto"], True, item["cor"])
                overlay.blit(surf, (x + 30, y_text))
            y_text += 22

        # Scrollbar
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

            # scroll_offset=0 => thumb embaixo
            # scroll_offset=max_scroll => thumb em cima
            fraction = self.scroll_offset / max_scroll
            thumb_y = track_y + int((1 - fraction) * usable_h)

            thumb = pygame.Rect(track_x, thumb_y, track_w, thumb_h)

        self._scroll_thumb_rect = thumb

        pygame.draw.rect(overlay, (55, 55, 65), track, border_radius=5)
        pygame.draw.rect(
            overlay,
            (0, 255, 150) if self._scroll_dragging else (120, 120, 130),
            thumb,
            border_radius=5
        )

        if self.carregando:
            loading = self.font_m.render("🤖 Pensando...", True, GOLD)
            overlay.blit(loading, (x + 30, y + self.altura - 90))

        input_y = y + self.altura - 60

        pygame.draw.rect(overlay, INPUT_BG, (x + 20, input_y, self.largura - 40, 40), border_radius=8)
        pygame.draw.rect(overlay, INPUT_BORDER, (x + 20, input_y, self.largura - 40, 40), 1, border_radius=8)

        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""

        texto_input = self.input_usuario if self.input_usuario else "Digite sua pergunta... (Enter para enviar)"
        txt_input = self.font_m.render(f"{texto_input}{cursor}", True, (0, 255, 150))

        overlay.blit(txt_input, (x + 35, input_y + 10))

        screen.blit(overlay, (0, 0))


def draw_chat_button(screen, x, y, w, h, is_optimal):
    cor = BLUE_NEON if is_optimal else (70, 70, 70)
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, cor, rect, border_radius=8)
    font = pygame.font.SysFont("arial", 16, bold=True)
    txt = "ABRIR CHAT IA" if is_optimal else "OTIMIZANDO..."
    surf = font.render(txt, True, WHITE)
    screen.blit(surf, (x + (w - surf.get_width()) // 2, y + (h - surf.get_height()) // 2))
    return rect


def draw_route_lines(screen, route):
    if len(route) < 2:
        return
    for i in range(len(route) - 1):
        pygame.draw.line(screen, BLUE_NEON, (route[i].x, route[i].y), (route[i + 1].x, route[i + 1].y), 3)


def draw_service_points(screen, points, font):
    """
    Desenha os pontos no mapa com:
    - cor pela prioridade
    - número sequencial da rota (1, 2, 3...) + código curto ao lado
    """
    if not points:
        return

    num_font = pygame.font.SysFont("arial", 11, bold=True)

    for idx, p in enumerate(points, start=1):
        center = (p.x, p.y)
        color = PRIORITY_COLORS.get(p.prioridade, WHITE)
        pygame.draw.circle(screen, color, center, 9)

        num_surf = num_font.render(str(idx), True, BLACK)
        num_rect = num_surf.get_rect(center=center)
        screen.blit(num_surf, num_rect)

        code_text = f"{p.codigo[:12]}"
        code_surf = font.render(code_text, True, BLACK)
        screen.blit(code_surf, (p.x + 12, p.y - 8))


def draw_side_panel(
    screen,
    px=None,
    pw=None,
    vh=None,
    f1=None,
    f2=None,
    route=None,
    gen=None,
    fit=None,
    dist_km=0.0,
    hist=None,
    scroll=0,
    opt=False,
    **kwargs,
):
    if px is None:
        px = kwargs.get("panel_x", 0)
    if pw is None:
        pw = kwargs.get("panel_width", 0)
    if vh is None:
        vh = kwargs.get("window_height", 0)
    if f1 is None:
        f1 = kwargs.get("title_font")
    if f2 is None:
        f2 = kwargs.get("text_font")
    if route is None:
        route = kwargs.get("route", [])
    if gen is None:
        gen = kwargs.get("generation", 0)
    if fit is None:
        fit = kwargs.get("best_fitness", 0.0)
    if hist is None:
        hist = kwargs.get("fitness_history", [])
    scroll = kwargs.get("scroll_offset", scroll)
    opt = kwargs.get("is_optimal", opt)

    if route is None:
        route = []

    pygame.draw.rect(screen, (30, 30, 30), (px, 0, pw, vh))
    pygame.draw.line(screen, BLUE_NEON, (px, 0), (px, vh), 2)

    margin = px + 20
    txt_gen = "ROTA OTIMIZADA!" if opt else f"GERAÇÃO: {gen}"
    screen.blit(f1.render(txt_gen, True, GOLD if opt else BLUE_NEON), (margin, 25))
    screen.blit(f2.render(f"Distância Total: {round(dist_km, 2)} km", True, WHITE), (margin, 55))
    screen.blit(f2.render(f"Custo (fitness): {round(fit, 2)}", True, GRAY_LIGHT), (margin, 72))

    pygame.draw.line(screen, (70, 70, 70), (px + 10, 85), (px + pw - 10, 85), 1)

    y_s = 100 - scroll

    for i, p in enumerate(route):
        if 80 < y_s < vh - 20:
            info_texto = f"{i + 1}. {p.codigo} | {p.tipo_atendimento} | {p.tempo_atendimento}h"
            cor = PRIORITY_COLORS.get(p.prioridade, WHITE)
            txt_surface = f2.render(info_texto, True, cor)
            screen.blit(txt_surface, (margin, y_s))

        y_s += 28


def draw_convergence_graph(screen, x, y, w, h, history):
    pygame.draw.rect(screen, (15, 15, 15), (x, y, w, h))
    pygame.draw.rect(screen, (80, 80, 80), (x, y, w, h), 1)

    font_mini = pygame.font.SysFont("arial", 10)
    font_label = pygame.font.SysFont("arial", 11, bold=True)

    label_y = font_label.render("CUSTO (FITNESS)", True, GRAY_LIGHT)
    screen.blit(label_y, (x - 10, y - 15))

    label_x = font_label.render("EVOLUÇÃO (GERAÇÕES)", True, GRAY_LIGHT)
    screen.blit(label_x, (x + w - 120, y + h + 5))

    if len(history) < 2:
        screen.blit(font_mini.render("Aguardando dados...", True, GRAY_LIGHT), (x + 10, y + h // 2))
        return

    for i in range(1, 5):
        gy = y + (h / 4) * i
        pygame.draw.line(screen, (40, 40, 40), (x, gy), (x + w, gy), 1)

    max_f, min_f = max(history), min(history)
    rng = max_f - min_f if max_f != min_f else 1

    points = []
    for i, f in enumerate(history):
        px = x + (i / (len(history) - 1)) * w
        py = y + h - ((f - min_f) / rng) * h
        points.append((px, py))

    pygame.draw.lines(screen, GOLD, False, points, 2)

    screen.blit(font_mini.render(f"{round(max_f, 1)}", True, GRAY_LIGHT), (x + w + 5, y))
    screen.blit(font_mini.render(f"{round(min_f, 1)}", True, GOLD), (x + w + 5, y + h - 10))