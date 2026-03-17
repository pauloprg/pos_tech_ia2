# -*- coding: utf-8 -*-
import pygame
import time # Necessário para o cursor piscar

# Cores
WHITE, BLACK, BLUE_NEON = (255, 255, 255), (20, 20, 20), (0, 191, 255)
GOLD, GRAY_DARK, GRAY_LIGHT = (255, 215, 0), (40, 40, 45), (150, 150, 150)
PRIORITY_COLORS = {4: (255, 50, 50), 3: (255, 165, 0), 2: (0, 200, 255), 1: (50, 255, 50)}

class BriefingPopup:
    def __init__(self, texto_inicial):
        self.historico_formatado = [] 
        self.input_usuario = ""
        self.largura, self.altura = 800, 550
        self.visivel = True
        self.carregando = False
        self.font_m = pygame.font.SysFont("arial", 16)
        self.font_t = pygame.font.SysFont("arial", 20, bold=True)
        self.adicionar_mensagem("IA", texto_inicial)

    def adicionar_mensagem(self, autor, texto):
        self.carregando = False
        prefixo = "🤖 Assistente: " if autor == "IA" else "👤 Maitê: "
        cor = (200, 230, 255) if autor == "IA" else WHITE
        palavras = (prefixo + texto).replace('\n', ' \n ').split(' ')
        linha_atual = ""
        for p in palavras:
            if p == '\n':
                self.historico_formatado.append({"texto": linha_atual, "cor": cor})
                linha_atual = ""
                continue
            test_line = linha_atual + p + " "
            if self.font_m.size(test_line)[0] < (self.largura - 60):
                linha_atual = test_line
            else:
                self.historico_formatado.append({"texto": linha_atual, "cor": cor})
                linha_atual = p + " "
        self.historico_formatado.append({"texto": linha_atual, "cor": cor})
        self.historico_formatado.append({"texto": "", "cor": BLACK})

    def draw(self, screen):
        if not self.visivel: return
        overlay = pygame.Surface((1400, 800), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), (0, 0, 1400, 800))
        x, y = (1000 - self.largura) // 2, (800 - self.altura) // 2
        rect = pygame.Rect(x, y, self.largura, self.altura)
        pygame.draw.rect(overlay, (25, 25, 30), rect, border_radius=15)
        pygame.draw.rect(overlay, BLUE_NEON, rect, 2, border_radius=15)
        overlay.blit(self.font_t.render("✨ Inteligência Logística - Llama 3", True, GOLD), (x+30, y+20))
        y_text = y + 70
        for item in self.historico_formatado[-16:]:
            if item["texto"]:
                surf = self.font_m.render(item["texto"], True, item["cor"])
                overlay.blit(surf, (x+30, y_text))
            y_text += 22
        input_y = y + self.altura - 60
        pygame.draw.rect(overlay, GRAY_DARK, (x+20, input_y, self.largura-40, 40), border_radius=8)
        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
        txt_input = self.font_m.render(f"Pergunta: {self.input_usuario}{cursor}", True, (0, 255, 150))
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
    for p in points:
        pygame.draw.circle(screen, PRIORITY_COLORS.get(p.prioridade, WHITE), (p.x, p.y), 9)

def draw_side_panel(screen, px, pw, vh, f1, f2, route, gen, fit, hist, scroll, opt):
    pygame.draw.rect(screen, (30, 30, 30), (px, 0, pw, vh))
    pygame.draw.line(screen, BLUE_NEON, (px, 0), (px, vh), 2)
    margin = px + 25
    txt_gen = "ROTA OTIMIZADA!" if opt else f"GERAÇÃO: {gen}"
    screen.blit(f1.render(txt_gen, True, GOLD if opt else BLUE_NEON), (margin, 25))
    screen.blit(f2.render(f"Distância: {round(fit, 2)} km", True, WHITE), (margin, 55))
    y_s = 100 - scroll
    for i, p in enumerate(route):
        if 100 < y_s < 520:
            pygame.draw.rect(screen, PRIORITY_COLORS.get(p.prioridade), (margin, y_s+4, 6, 12))
            screen.blit(f2.render(f"{i+1}º: {p.codigo[:28]}", True, WHITE), (margin+15, y_s))
        y_s += 25
    gx, gy, gw, gh = px + 50, 620, pw - 80, 140
    pygame.draw.rect(screen, (20,20,20), (gx, gy, gw, gh))
    if len(hist) > 2:
        max_h, min_h = max(hist), min(hist)
        pts = [(gx+(i*gw/len(hist)), (gy+gh)-((val-min_h)/(max_h-min_h+1)*gh)) for i,val in enumerate(hist)]
        pygame.draw.lines(screen, GOLD if opt else BLUE_NEON, False, pts, 2)