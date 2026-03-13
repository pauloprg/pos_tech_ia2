# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:48:04 2026

@author: paulo.goncalves
"""

from dataclasses import dataclass


@dataclass
class ServicePoint:
    id: int
    x: int
    y: int
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