"""
antivravity_core.py — Motor de Inteligência do Hub de Inovação VIX
Centraliza o processamento do portfólio de iniciativas e cálculo de KPIs utilizando dataclasses.
Suporta simulação de dados em tempo real.
"""

import random
from dataclasses import dataclass, asdict
from datetime import datetime
from copy import deepcopy

@dataclass
class Iniciativa:
    id: int
    nome: str
    area: str
    status: str
    roi: float
    tem_indicador: bool
    responsavel: str
    prioridade: str
    horas: int

# Base de dados simulada de iniciativas (que depois você pode conectar num banco real)
DB_INICIATIVAS = [
    Iniciativa(
        id=1,
        nome="Automação de Relatórios",
        area="TI",
        status="Concluída",
        roi=4200.0,
        tem_indicador=True,
        responsavel="Ana Lima",
        prioridade="Alta",
        horas=60,
    ),
    Iniciativa(
        id=2,
        nome="Migração Cloud",
        area="Infra",
        status="Em Andamento",
        roi=75000.0,
        tem_indicador=True,
        responsavel="Carlos Souza",
        prioridade="Alta",
        horas=120,
    ),
    Iniciativa(
        id=3,
        nome="Treinamento RH Digital",
        area="RH",
        status="Planejada",
        roi=0.0,
        tem_indicador=False,
        responsavel="Mariana Costa",
        prioridade="Média",
        horas=10,
    ),
    Iniciativa(
        id=4,
        nome="BI Comercial",
        area="Comercial",
        status="Em Andamento",
        roi=18500.0,
        tem_indicador=True,
        responsavel="Pedro Alves",
        prioridade="Alta",
        horas=85,
    ),
    Iniciativa(
        id=5,
        nome="Portal do Colaborador",
        area="TI",
        status="Em Andamento",
        roi=9800.0,
        tem_indicador=True,
        responsavel="Julia Nunes",
        prioridade="Média",
        horas=200,
    ),
    Iniciativa(
        id=6,
        nome="Processo de Onboarding",
        area="RH",
        status="Planejada",
        roi=2100.0,
        tem_indicador=False,
        responsavel="Fernanda Dias",
        prioridade="Baixa",
        horas=30,
    ),
]

def get_dados_iniciativas() -> list[dict]:
    """Retorna os dados base convertidos em dicionários para compatibilidade com serialização."""
    return [asdict(i) for i in DB_INICIATIVAS]

def get_dados_realtime() -> list[dict]:
    """
    Simula leitura em tempo real aplicando variações realistas a cada ciclo.
    Retorna uma lista de dicionários correspondentes às iniciativas modificadas.
    """
    dados = deepcopy(DB_INICIATIVAS)

    for i in dados:
        if i.roi > 0:
            # Variação de ±3% no ROI (simula oscilação de câmbio/custo)
            fator = random.uniform(0.97, 1.03)
            i.roi = round(i.roi * fator, 2)

        if i.horas > 0:
            # Variação de ±2h nas horas (simula registro de ponto)
            delta = random.randint(-2, 2)
            i.horas = max(0, i.horas + delta)

        # Pequena chance de progressão de status
        if i.status == "Planejada" and random.random() < 0.05:
            i.status = "Em Andamento"
        elif i.status == "Em Andamento" and random.random() < 0.03:
            i.status = "Concluída"
            i.tem_indicador = True

    return [asdict(item) for item in dados]

def calcular_kpis(iniciativas: list[dict]) -> dict:
    """Processa o portfólio de iniciativas e retorna os KPIs do Hub."""
    if not iniciativas:
        return {
            "roi": 0.0,
            "horas": 0,
            "governanca": 0.0,
            "total": 0,
            "em_andamento": 0,
            "concluidas": 0,
            "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

    roi_total = sum(i.get("roi", 0.0) for i in iniciativas)
    horas_total = sum(i.get("horas", 0) for i in iniciativas)

    com_indicador = len([i for i in iniciativas if i.get("tem_indicador")])
    taxa_governanca = (com_indicador / len(iniciativas)) * 100

    em_andamento = len([i for i in iniciativas if i.get("status") == "Em Andamento"])
    concluidas = len([i for i in iniciativas if i.get("status") == "Concluída"])

    return {
        "roi": roi_total,
        "horas": horas_total,
        "governanca": round(taxa_governanca, 1),
        "total": len(iniciativas),
        "em_andamento": em_andamento,
        "concluidas": concluidas,
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }

def filtrar_por_area(iniciativas: list[dict], area: str) -> list[dict]:
    """Filtra iniciativas por área de negócio."""
    if area == "Todas":
        return iniciativas
    return [i for i in iniciativas if i.get("area") == area]

def get_areas_disponiveis(iniciativas: list[dict]) -> list[str]:
    """Retorna lista única de áreas cadastradas."""
    areas = sorted(set(i.get("area", "") for i in iniciativas))
    return ["Todas"] + areas

def formatar_roi(valor: float) -> str:
    """Formata valor monetário em reais."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
