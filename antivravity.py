"""
antivravity.py — Motor de Inteligência do Hub de Inovação VIX
Centraliza toda a lógica de negócio: processamento de portfólio e cálculo de KPIs.
Suporta simulação de dados em tempo real para demonstração ao vivo.
"""

import random
from datetime import datetime
from copy import deepcopy

# Base fixa do portfólio
_BASE_INICIATIVAS = [
    {
        "nome": "Automação de Relatórios",
        "roi": 4200,
        "horas": 60,
        "indicador_definido": True,
        "area": "TI",
        "status": "Concluída",
        "responsavel": "Ana Lima",
        "prioridade": "Alta",
    },
    {
        "nome": "Migração Cloud",
        "roi": 75000,
        "horas": 120,
        "indicador_definido": True,
        "area": "Infra",
        "status": "Em Andamento",
        "responsavel": "Carlos Souza",
        "prioridade": "Alta",
    },
    {
        "nome": "Treinamento RH Digital",
        "roi": 0,
        "horas": 10,
        "indicador_definido": False,
        "area": "RH",
        "status": "Planejada",
        "responsavel": "Mariana Costa",
        "prioridade": "Média",
    },
    {
        "nome": "BI Comercial",
        "roi": 18500,
        "horas": 85,
        "indicador_definido": True,
        "area": "Comercial",
        "status": "Em Andamento",
        "responsavel": "Pedro Alves",
        "prioridade": "Alta",
    },
    {
        "nome": "Portal do Colaborador",
        "roi": 9800,
        "horas": 200,
        "indicador_definido": True,
        "area": "TI",
        "status": "Em Andamento",
        "responsavel": "Julia Nunes",
        "prioridade": "Média",
    },
    {
        "nome": "Processo de Onboarding",
        "roi": 2100,
        "horas": 30,
        "indicador_definido": False,
        "area": "RH",
        "status": "Planejada",
        "responsavel": "Fernanda Dias",
        "prioridade": "Baixa",
    },
]


def get_dados_iniciativas() -> list:
    """Retorna os dados base sem variação."""
    return deepcopy(_BASE_INICIATIVAS)


def get_dados_realtime() -> list:
    """
    Simula leitura em tempo real do motor Antivravity.
    Aplica variações realistas a cada ciclo para simular
    integração com sistemas vivos (ERP, BI, APIs).
    """
    dados = deepcopy(_BASE_INICIATIVAS)

    for i in dados:
        if i["roi"] > 0:
            # Variação de ±3% no ROI (simula oscilação de câmbio/custo)
            fator = random.uniform(0.97, 1.03)
            i["roi"] = int(i["roi"] * fator)

        if i["horas"] > 0:
            # Variação de ±2h nas horas (simula registro de ponto)
            delta = random.randint(-2, 2)
            i["horas"] = max(0, i["horas"] + delta)

        # Pequena chance de progressão de status
        if i["status"] == "Planejada" and random.random() < 0.05:
            i["status"] = "Em Andamento"
        elif i["status"] == "Em Andamento" and random.random() < 0.03:
            i["status"] = "Concluída"
            i["indicador_definido"] = True

    return dados


def calcular_kpis(iniciativas: list) -> dict:
    """Processa o portfólio de iniciativas e retorna os KPIs do Hub."""
    if not iniciativas:
        return {
            "roi": 0,
            "horas": 0,
            "governanca": 0.0,
            "total": 0,
            "em_andamento": 0,
            "concluidas": 0,
            "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

    roi_total = sum(i.get("roi", 0) for i in iniciativas)
    horas_total = sum(i.get("horas", 0) for i in iniciativas)

    com_indicador = len([i for i in iniciativas if i.get("indicador_definido")])
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


def filtrar_por_area(iniciativas: list, area: str) -> list:
    """Filtra iniciativas por área de negócio."""
    if area == "Todas":
        return iniciativas
    return [i for i in iniciativas if i.get("area") == area]


def get_areas_disponiveis(iniciativas: list) -> list:
    """Retorna lista única de áreas cadastradas."""
    areas = sorted(set(i.get("area", "") for i in iniciativas))
    return ["Todas"] + areas


def formatar_roi(valor: int) -> str:
    """Formata valor monetário em reais."""
    return f"R$ {valor:,.0f}".replace(",", ".")
