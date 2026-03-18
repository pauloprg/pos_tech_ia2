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

        self.font_m = pygame.font.SysFont("arial", 16)
        self.font_t = pygame.font.SysFont("arial", 20, bold=True)

        self.adicionar_mensagem("IA", texto_inicial)

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

        y_text = y + 70
        start = max(0, len(self.historico_formatado) - self.max_linhas_visiveis - self.scroll_offset)
        end = start + self.max_linhas_visiveis

        for item in self.historico_formatado[start:end]:
            if item["texto"]:
                surf = self.font_m.render(item["texto"], True, item["cor"])
                overlay.blit(surf, (x+30, y_text))
            y_text += 22

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

def draw_chat_button(screen, x, y, w, h, is_optimal):
    cor = BLUE_NEON if is_optimal else (70, 70, 70)
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, cor, rect, border_radius=8)
    font = pygame.font.SysFont("arial", 16, bold=True)
    txt = "ABRIR CHAT IA" if is_optimal else "OTIMIZANDO..."
    surf = font.render(txt, True, WHITE)
    screen.blit(surf, (x + (w - surf.get_width())//2, y + (h - surf.get_height())//2))
    return rect

def draw_route_lines(screen, route):
    if len(route) < 2: return
    for i in range(len(route) - 1):
        # Use route[i].x e y, que são os pixels calculados
        pygame.draw.line(screen, BLUE_NEON, (route[i].x, route[i].y), (route[i+1].x, route[i+1].y), 3)

def draw_service_points(screen, points, font):
    """
    Desenha os pontos no mapa com:
    - cor pela prioridade
    - número sequencial da rota (1, 2, 3...) + código curto ao lado

    A ordem é dada pela lista `points` recebida. Para mostrar a ordem da
    rota ótima, basta passar `best_route` em vez de `service_points`.
    """
    if not points:
        return

    for idx, p in enumerate(points, start=1):
        center = (p.x, p.y)
        color = PRIORITY_COLORS.get(p.prioridade, WHITE)
        pygame.draw.circle(screen, color, center, 9)

        # Número da ordem (negrito, sobre o ponto)
        num_font = pygame.font.SysFont("arial", 11, bold=True)
        num_surf = num_font.render(str(idx), True, BLACK)
        num_rect = num_surf.get_rect(center=center)
        screen.blit(num_surf, num_rect)

        # Código curto ao lado do ponto
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
    # Compatibilidade com chamadas usando keywords (ex: panel_x/panel_width/window_height)
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
    # Desenha o fundo do painel
    pygame.draw.rect(screen, (30, 30, 30), (px, 0, pw, vh))
    pygame.draw.line(screen, BLUE_NEON, (px, 0), (px, vh), 2)
    
    margin = px + 20
    txt_gen = "ROTA OTIMIZADA!" if opt else f"GERAÇÃO: {gen}"
    screen.blit(f1.render(txt_gen, True, GOLD if opt else BLUE_NEON), (margin, 25))
    screen.blit(f2.render(f"Distância Total: {round(dist_km, 2)} km", True, WHITE), (margin, 55))
    screen.blit(f2.render(f"Custo (fitness): {round(fit, 2)}", True, GRAY_LIGHT), (margin, 72))
    
    # Linha separadora
    pygame.draw.line(screen, (70, 70, 70), (px + 10, 85), (px + pw - 10, 85), 1)

    # Início da lista de pontos
    y_s = 100 - scroll
    
    for i, p in enumerate(route):
        # Só renderiza se estiver dentro da visão vertical da tela para evitar erros de blit
        if 80 < y_s < vh - 20:
            # Texto solicitado: Ordem, Código, Tipo e Tempo
            # Ex: 1. CEI-123 | Parto | 0.5h
            info_texto = f"{i+1}. {p.codigo} | {p.tipo_atendimento} | {p.tempo_atendimento}h"
            
            # Cor baseada na prioridade (usando seu dicionário PRIORITY_COLORS)
            cor = PRIORITY_COLORS.get(p.prioridade, WHITE)
            
            # Renderização
            txt_surface = f2.render(info_texto, True, cor)
            screen.blit(txt_surface, (margin, y_s))
        
        y_s += 28 # Espaçamento entre as linhas


def draw_convergence_graph(screen, x, y, w, h, history):
    """Desenha o gráfico de evolução com labels nos eixos X e Y."""
    # Fundo e borda do gráfico
    pygame.draw.rect(screen, (15, 15, 15), (x, y, w, h))
    pygame.draw.rect(screen, (80, 80, 80), (x, y, w, h), 1)
    
    font_mini = pygame.font.SysFont("arial", 10)
    font_label = pygame.font.SysFont("arial", 11, bold=True)

    # Labels dos Eixos
    # Eixo Y (Custo) - Rotacionado visualmente pelo contexto
    label_y = font_label.render("CUSTO (FITNESS)", True, GRAY_LIGHT)
    screen.blit(label_y, (x - 10, y - 15))
    
    # Eixo X (Gerações)
    label_x = font_label.render("EVOLUÇÃO (GERAÇÕES)", True, GRAY_LIGHT)
    screen.blit(label_x, (x + w - 120, y + h + 5))

    if len(history) < 2:
        screen.blit(font_mini.render("Aguardando dados...", True, GRAY_LIGHT), (x + 10, y + h//2))
        return

    # Grade de fundo
    for i in range(1, 5):
        gy = y + (h / 4) * i
        pygame.draw.line(screen, (40, 40, 40), (x, gy), (x + w, gy), 1)

    max_f, min_f = max(history), min(history)
    rng = max_f - min_f if max_f != min_f else 1
    
    points = []
    for i, f in enumerate(history):
        px = x + (i / (len(history)-1)) * w
        py = y + h - ((f - min_f) / rng) * h
        points.append((px, py))
    
    # Linha de evolução Amarela
    pygame.draw.lines(screen, GOLD, False, points, 2)
    
    # Valores de referência nos cantos
    screen.blit(font_mini.render(f"{round(max_f,1)}", True, GRAY_LIGHT), (x + w + 5, y))
    screen.blit(font_mini.render(f"{round(min_f,1)}", True, GOLD), (x + w + 5, y + h - 10))