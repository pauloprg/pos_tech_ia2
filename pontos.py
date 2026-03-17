# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass
class ServicePoint:
    id: int
    x: int
    y: int
    lat: float # <--- ADICIONADO
    lon: float # <--- ADICIONADO
    codigo: str
    tipo_atendimento: str
    prioridade: int
    quantidade: int
    tempo_inicio: int
    tempo_fim: int
    tempo_atendimento: float
    temperatura_controlada: bool
    protocolo_especial: bool

    def posicao(self) -> tuple[int, int]:
        return (self.x, self.y)