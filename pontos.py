# pontos.py
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Tuple, Set


@dataclass(frozen=True)
class ServicePoint:
    id: int
    lat: float
    lon: float
    x: int
    y: int
    lat: float
    lon: float
    codigo: str
    tipo_atendimento: str
    prioridade: int                  # 4 = máxima, 1 = menor
    quantidade: int                  # quantidade total de suprimentos/unidades
    tempo_inicio: int                # início da janela (hora)
    tempo_fim: int                   # fim da janela (hora)
    tempo_atendimento: float         # horas
    temperatura_controlada: bool
    protocolo_especial: bool
    tipos_veiculo_permitidos: Set[str] = field(default_factory=set)

    def posicao(self) -> Tuple[int, int]:
        return (self.x, self.y)


@dataclass(frozen=True)
class Depot:
    x: int
    y: int
    lat: float
    lon: float
    nome: str = "Base Central"


@dataclass(frozen=True)
class Vehicle:
    id: int
    nome: str
    tipo: str                        # "moto", "van_refrigerada", "ambulancia", "drone"
    velocidade_kmh: float
    custo_km: float
    capacidade_suprimentos: int
    max_paradas: int
    max_distancia_km: float
    tipos_atendimento: Set[str]
    suporta_temperatura_controlada: bool
    suporta_protocolo_especial: bool

    def pode_atender(self, ponto: ServicePoint) -> bool:
        if ponto.tipos_veiculo_permitidos and self.tipo not in ponto.tipos_veiculo_permitidos:
            return False

        if ponto.tipo_atendimento not in self.tipos_atendimento:
            return False

        if ponto.temperatura_controlada and not self.suporta_temperatura_controlada:
            return False

        if ponto.protocolo_especial and not self.suporta_protocolo_especial:
            return False

        if ponto.quantidade > self.capacidade_suprimentos:
            return False

        return True