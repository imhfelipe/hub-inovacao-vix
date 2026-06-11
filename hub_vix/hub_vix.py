"""
hub_vix.py — Interface Reativa do Hub de Inovação VIX
Estilizado nos padrões do Nexus-OS com sidebar de monitoramento, clock, sparklines e reatividade.
"""

import asyncio
from typing import TypedDict, List, Dict
from datetime import datetime

import reflex as rx
from reflex_base.event import BACKGROUND_TASK_MARKER
from .antivravity_core import (
    calcular_kpis,
    get_dados_iniciativas,
    get_dados_realtime,
    filtrar_por_area,
    get_areas_disponiveis,
    formatar_roi,
)
from . import style


def background(fn):
    """Decorator que marca uma coroutine como background task no Reflex 0.9."""
    setattr(fn, BACKGROUND_TASK_MARKER, True)
    return fn


# ─────────────────────────────────────────────
# TIPOS
# ─────────────────────────────────────────────

class Iniciativa(TypedDict):
    id: int
    nome: str
    area: str
    status: str
    roi: float
    tem_indicador: bool
    responsavel: str
    prioridade: str
    horas: int
    roi_fmt: str


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────

class DashboardState(rx.State):
    """Estado global com atualização em tempo real, memória histórica e tendências."""

    iniciativas_raw: list[Iniciativa] = get_dados_iniciativas()
    area_selecionada: str = "Todas"

    # Controles de tempo real
    is_live: bool = True
    intervalo_seg: int = 5
    relogio: str = datetime.now().strftime("%H:%M:%S")
    tick: int = 0  # contador de ticks

    # Memória histórica para micro-indicadores de tendência (semana anterior simulada)
    prev_roi: float = float(calcular_kpis(get_dados_iniciativas())["roi"])
    prev_horas: float = float(calcular_kpis(get_dados_iniciativas())["horas"])
    prev_governanca: float = float(calcular_kpis(get_dados_iniciativas())["governanca"])

    # Histórico dos Sparklines
    roi_history: list[dict] = [
        {"tick": 1, "val": 85000.0},
        {"tick": 2, "val": 92000.0},
        {"tick": 3, "val": 90000.0},
        {"tick": 4, "val": 98000.0},
        {"tick": 5, "val": 95000.0},
        {"tick": 6, "val": 102000.0},
        {"tick": 7, "val": 109600.0},
        {"tick": 8, "val": 109600.0},
        {"tick": 9, "val": 109600.0},
        {"tick": 10, "val": 109600.0},
    ]
    horas_history: list[dict] = [
        {"tick": 1, "val": 420},
        {"tick": 2, "val": 450},
        {"tick": 3, "val": 440},
        {"tick": 4, "val": 480},
        {"tick": 5, "val": 470},
        {"tick": 6, "val": 490},
        {"tick": 7, "val": 505},
        {"tick": 8, "val": 505},
        {"tick": 9, "val": 505},
        {"tick": 10, "val": 505},
    ]
    governanca_history: list[dict] = [
        {"tick": 1, "val": 50.0},
        {"tick": 2, "val": 50.0},
        {"tick": 3, "val": 66.7},
        {"tick": 4, "val": 66.7},
        {"tick": 5, "val": 66.7},
        {"tick": 6, "val": 66.7},
        {"tick": 7, "val": 66.7},
        {"tick": 8, "val": 66.7},
        {"tick": 9, "val": 66.7},
        {"tick": 10, "val": 66.7},
    ]
    total_history: list[dict] = [
        {"tick": 1, "val": 5},
        {"tick": 2, "val": 5},
        {"tick": 3, "val": 6},
        {"tick": 4, "val": 6},
        {"tick": 5, "val": 6},
        {"tick": 6, "val": 6},
        {"tick": 7, "val": 6},
        {"tick": 8, "val": 6},
        {"tick": 9, "val": 6},
        {"tick": 10, "val": 6},
    ]

    # ── Vars derivadas de KPIs ────────────────

    @rx.var
    def iniciativas(self) -> list[Iniciativa]:
        return filtrar_por_area(self.iniciativas_raw, self.area_selecionada)

    @rx.var
    def areas(self) -> list[str]:
        return get_areas_disponiveis(self.iniciativas_raw)

    @rx.var
    def kpi_roi_fmt(self) -> str:
        return formatar_roi(calcular_kpis(self.iniciativas).get("roi", 0.0))

    @rx.var
    def kpi_horas(self) -> int:
        return calcular_kpis(self.iniciativas).get("horas", 0)

    @rx.var
    def kpi_governanca(self) -> float:
        return calcular_kpis(self.iniciativas).get("governanca", 0.0)

    @rx.var
    def kpi_total(self) -> int:
        return calcular_kpis(self.iniciativas).get("total", 0)

    # ── Vars para Gráfico Donut ────────────────

    @rx.var
    def status_dist(self) -> List[Dict]:
        k = calcular_kpis(self.iniciativas)
        em_andamento = k.get("em_andamento", 0)
        concluidas = k.get("concluidas", 0)
        planejadas = k.get("total", 0) - em_andamento - concluidas
        return [
            {"name": "Concluídas", "value": concluidas},
            {"name": "Em Andamento", "value": em_andamento},
            {"name": "Planejadas", "value": planejadas},
        ]

    # ── Var para Gráfico de Performance ─────────

    @rx.var
    def performance_evolution(self) -> List[Dict]:
        res = []
        for i in range(10):
            r_val = self.roi_history[i]["val"]
            h_val = self.horas_history[i]["val"]
            res.append({
                "tick": f"T{i+1}",
                "ROI (kR$)": round(r_val / 1000, 1),
                "Esforço (h)": h_val
            })
        return res

    # ── Micro-indicadores de Tendência ─────────

    @rx.var
    def roi_atual(self) -> float:
        return float(calcular_kpis(self.iniciativas).get("roi", 0.0))

    @rx.var
    def horas_atual(self) -> float:
        return float(calcular_kpis(self.iniciativas).get("horas", 0))

    @rx.var
    def governanca_atual(self) -> float:
        return float(calcular_kpis(self.iniciativas).get("governanca", 0.0))

    @rx.var
    def roi_trend_icon(self) -> rx.Var:
        curr = self.roi_atual
        prev = self.prev_roi
        return rx.cond(curr > prev, "arrow-up-right", rx.cond(curr < prev, "arrow-down-right", "minus"))

    @rx.var
    def roi_trend_color(self) -> rx.Var:
        curr = self.roi_atual
        prev = self.prev_roi
        return rx.cond(curr > prev, style.COLOR_GREEN, rx.cond(curr < prev, style.COLOR_ROSE, style.COLOR_GRAY))

    @rx.var
    def horas_trend_icon(self) -> rx.Var:
        curr = self.horas_atual
        prev = self.prev_horas
        return rx.cond(curr > prev, "arrow-up-right", rx.cond(curr < prev, "arrow-down-right", "minus"))

    @rx.var
    def horas_trend_color(self) -> rx.Var:
        curr = self.horas_atual
        prev = self.prev_horas
        return rx.cond(curr > prev, style.COLOR_GREEN, rx.cond(curr < prev, style.COLOR_ROSE, style.COLOR_GRAY))

    @rx.var
    def governanca_trend_icon(self) -> rx.Var:
        curr = self.governanca_atual
        prev = self.prev_governanca
        return rx.cond(curr > prev, "arrow-up-right", rx.cond(curr < prev, "arrow-down-right", "minus"))

    @rx.var
    def governanca_trend_color(self) -> rx.Var:
        curr = self.governanca_atual
        prev = self.prev_governanca
        return rx.cond(curr > prev, style.COLOR_GREEN, rx.cond(curr < prev, style.COLOR_ROSE, style.COLOR_GRAY))

    @rx.var
    def live_label(self) -> str:
        return "● AO VIVO" if self.is_live else "⏸ PAUSADO"

    @rx.var
    def live_color(self) -> str:
        return style.COLOR_GREEN if self.is_live else "#f59e0b"

    # ── Background: loop de tempo real ────────

    def guardar_historico(self):
        """Salva a leitura de KPIs anterior para calcular tendências antes de puxar dados novos."""
        k = calcular_kpis(self.iniciativas)
        self.prev_roi = float(k.get("roi", 0.0))
        self.prev_horas = float(k.get("horas", 0))
        self.prev_governanca = float(k.get("governanca", 0.0))

    def atualizar_historico_sparklines(self):
        """Atualiza a série temporal dos mini-gráficos com base nos novos valores de KPI."""
        k = calcular_kpis(self.iniciativas)
        r_val = float(k.get("roi", 0.0))
        h_val = float(k.get("horas", 0))
        g_val = float(k.get("governanca", 0.0))
        t_val = int(k.get("total", 0))
        
        self.roi_history = self.roi_history[1:] + [{"tick": self.tick, "val": r_val}]
        self.horas_history = self.horas_history[1:] + [{"tick": self.tick, "val": h_val}]
        self.governanca_history = self.governanca_history[1:] + [{"tick": self.tick, "val": g_val}]
        self.total_history = self.total_history[1:] + [{"tick": self.tick, "val": t_val}]

    @background
    async def iniciar_live(self):
        """
        Loop assíncrono que roda enquanto o usuário está na página.
        Atualiza dados e relógio a cada N segundos.
        """
        while True:
            await asyncio.sleep(1)  # tick a cada 1s para o relógio
            async with self:
                self.relogio = datetime.now().strftime("%H:%M:%S")
                self.tick += 1
                # A cada `intervalo_seg` ticks, busca novos dados
                if self.is_live and self.tick % self.intervalo_seg == 0:
                    self.guardar_historico()
                    self.iniciativas_raw = get_dados_realtime()
                    self.atualizar_historico_sparklines()

    # ── Ações do usuário ──────────────────────

    def toggle_live(self):
        self.is_live = not self.is_live

    def selecionar_area(self, area: str):
        self.area_selecionada = area

    def set_intervalo(self, valor: str):
        try:
            self.intervalo_seg = int(valor)
        except ValueError:
            self.intervalo_seg = 5

    def atualizar_agora(self):
        self.guardar_historico()
        self.iniciativas_raw = get_dados_realtime()
        self.atualizar_historico_sparklines()


# ─────────────────────────────────────────────
# COMPONENTES PREMIUM DESIGN SYSTEM (NEXUS-OS STYLE)
# ─────────────────────────────────────────────

def badge_status(status: str) -> rx.Component:
    """Badge de status com ícone interno dinâmico."""
    return rx.cond(
        status == "Concluída",
        rx.badge(
            rx.hstack(
                rx.icon("circle-check", size=12),
                rx.text("Concluída", size="1"),
                spacing="1",
                align="center",
            ),
            color_scheme="green",
            variant="soft",
            radius="full",
            padding_x="2",
        ),
        rx.cond(
            status == "Em Andamento",
            rx.badge(
                rx.hstack(
                    rx.icon("clock", size=12),
                    rx.text("Em Andamento", size="1"),
                    spacing="1",
                    align="center",
                ),
                color_scheme="cyan",
                variant="soft",
                radius="full",
                padding_x="2",
            ),
            rx.badge(
                rx.hstack(
                    rx.icon("calendar", size=12),
                    rx.text("Planejada", size="1"),
                    spacing="1",
                    align="center",
                ),
                color_scheme="orange",
                variant="soft",
                radius="full",
                padding_x="2",
            ),
        ),
    )


def badge_prioridade(prioridade: str) -> rx.Component:
    """Badge de prioridade estilizada."""
    return rx.badge(
        prioridade,
        color_scheme=rx.cond(
            prioridade == "Alta", "ruby",
            rx.cond(prioridade == "Média", "amber", "gray")
        ),
        variant="outline",
        radius="full",
        padding_x="2",
        padding_y="0.5",
        weight="medium",
    )


def kpi_card(label: str, valor, icon: str, cor: str, border_left: str, history_data, trend_icon: str = "", trend_color: str = "") -> rx.Component:
    """Card de KPI com visual Nexus-OS Sparkline e Text Glow."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, color=cor, size=16),
                rx.text(label, size="1", color=style.COLOR_GRAY, weight="medium"),
                justify="start",
                width="100%",
                align="center",
            ),
            rx.hstack(
                rx.text(
                    valor,
                    size="7",
                    weight="bold",
                    color=style.COLOR_TEXT,
                    font_family=style.FONT_FAMILY_MONO,
                    text_shadow=f"0 0 20px {cor}30",
                    margin_top="1",
                ),
                rx.cond(
                    trend_icon != "",
                    rx.box(
                        rx.cond(
                            trend_icon == "arrow-up-right",
                            rx.icon("arrow-up-right", color=trend_color, size=16),
                            rx.cond(
                                trend_icon == "arrow-down-right",
                                rx.icon("arrow-down-right", color=trend_color, size=16),
                                rx.icon("minus", color=trend_color, size=16)
                            )
                        ),
                        margin_top="2",
                        margin_left="1",
                    ),
                ),
                align="center",
                width="100%",
            ),
            # Sparkline acoplado na base do card
            rx.box(
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="val",
                        stroke=cor,
                        fill=f"{cor}20",
                        stroke_width=1.5,
                        dot=False,
                    ),
                    data=history_data,
                    height=45,
                    width="100%",
                ),
                width="100%",
                margin_top="3",
                padding="0",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        width="100%",
        variant="classic",
        background_color=style.CARD_BG,
        border=f"1px solid {style.CARD_BORDER}",
        border_left=border_left,
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.4)",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": f"0 12px 24px -10px rgba(0,0,0,0.6), 0 0 16px {cor}15",
            "border_color": f"{cor}40",
        },
        padding_top="4",
        padding_x="4",
        padding_bottom="0",  # Sit clean layout do Sparkline
        border_radius="xl",
        overflow="hidden",
    )


def performance_chart_card() -> rx.Component:
    """Card do Gráfico Principal de Evolução Comparativa (Nexus Telemetry)."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Nexus Telemetry · Performance do Portfólio", size="2", color=style.COLOR_TEXT, weight="bold", font_family=style.FONT_FAMILY_MONO),
                    rx.text("Evolução temporal comparativa: ROI Acumulado (em milhares) vs Esforço total", size="1", color=style.COLOR_GRAY),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.badge("Live Telemetry", variant="outline", color_scheme="cyan", radius="full"),
                width="100%",
                align="center",
            ),
            rx.recharts.area_chart(
                rx.recharts.area(
                    data_key="ROI (kR$)",
                    stroke=style.COLOR_CYAN,
                    fill=f"{style.COLOR_CYAN}20",
                    stroke_width=2,
                    dot=False,
                ),
                rx.recharts.area(
                    data_key="Esforço (h)",
                    stroke=style.COLOR_PURPLE,
                    fill=f"{style.COLOR_PURPLE}20",
                    stroke_width=2,
                    dot=False,
                ),
                rx.recharts.x_axis(data_key="tick", stroke=style.COLOR_GRAY, style={"fontSize": "10px"}),
                rx.recharts.y_axis(stroke=style.COLOR_GRAY, style={"fontSize": "10px"}),
                rx.recharts.legend(),
                rx.recharts.tooltip(),
                data=DashboardState.performance_evolution,
                height=180,
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        variant="classic",
        background_color=style.CARD_BG,
        border=f"1px solid {style.CARD_BORDER}",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.4)",
        padding="5",
        border_radius="xl",
        width="100%",
    )


def donut_chart_card() -> rx.Component:
    """Card de Gráfico Donut de Status (Nexus-OS Style)."""
    return rx.card(
        rx.vstack(
            rx.text("Distribuição por Status", size="2", color=style.COLOR_GRAY, weight="medium", font_family=style.FONT_FAMILY_MONO),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    rx.recharts.cell(fill=style.COLOR_GREEN),  # Concluídas - Green
                    rx.recharts.cell(fill=style.COLOR_CYAN),   # Em Andamento - Cyan
                    rx.recharts.cell(fill=style.COLOR_ROSE),   # Planejadas - Rose
                    data=DashboardState.status_dist,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    inner_radius=45,
                    outer_radius=65,
                    padding_angle=5,
                ),
                rx.recharts.legend(
                    vertical_align="bottom",
                    height=30,
                ),
                rx.recharts.tooltip(),
                width="100%",
                height=180,
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        variant="classic",
        background_color=style.CARD_BG,
        border=f"1px solid {style.CARD_BORDER}",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.4)",
        padding="5",
        border_radius="xl",
        width="100%",
        height="100%",
    )


def linha_iniciativa(iniciativa: Iniciativa) -> rx.Component:
    """Uma linha estilizada para o Grid/Tabela de Governança."""
    return rx.table.row(
        rx.table.cell(
            rx.text(iniciativa["nome"], weight="medium", size="2", color="#f1f5f9")
        ),
        rx.table.cell(
            rx.badge(
                iniciativa["area"],
                variant="surface",
                radius="medium",
                color_scheme="indigo",
                size="1",
            )
        ),
        rx.table.cell(
            rx.text(iniciativa["responsavel"], size="2", color=style.COLOR_GRAY)
        ),
        rx.table.cell(badge_status(iniciativa["status"])),
        rx.table.cell(badge_prioridade(iniciativa["prioridade"])),
        rx.table.cell(
            rx.text(
                iniciativa["roi_fmt"],
                weight="bold",
                size="2",
                color=rx.cond(iniciativa["roi"] > 0, style.COLOR_GREEN, style.COLOR_GRAY),
            ),
        ),
        rx.table.cell(
            rx.cond(
                iniciativa["tem_indicador"],
                rx.icon("circle-check", color=style.COLOR_GREEN, size=18),
                rx.icon("circle-alert", color=style.COLOR_ROSE, size=18),
            )
        ),
        align="center",
        _hover={"background_color": "rgba(255, 255, 255, 0.025)"},
        transition="background-color 0.2s ease",
    )


def filtros_area() -> rx.Component:
    """Selector de áreas com efeito gradiente no botão ativo e borda suave no inativo."""
    return rx.hstack(
        rx.foreach(
            DashboardState.areas,
            lambda area: rx.button(
                area,
                on_click=DashboardState.selecionar_area(area),
                background=rx.cond(
                    DashboardState.area_selecionada == area,
                    style.GRADIENT_NEXUS,
                    "transparent"
                ),
                border=rx.cond(
                    DashboardState.area_selecionada == area,
                    "none",
                    f"1px solid {style.CARD_BORDER}"
                ),
                color=rx.cond(DashboardState.area_selecionada == area, "#ffffff", style.COLOR_GRAY),
                radius="full",
                size="2",
                cursor="pointer",
                _hover={
                    "opacity": "0.9",
                    "border_color": "rgba(255, 255, 255, 0.35)"
                },
            ),
        ),
        spacing="2",
        wrap="wrap",
    )


def controles_live() -> rx.Component:
    """Barra de controle em tempo real do estilo SaaS (Glassmorphism)."""
    return rx.card(
        rx.hstack(
            # Indicador de atividade
            rx.hstack(
                rx.box(
                    class_name=rx.cond(DashboardState.is_live, "pulse-dot", ""),
                    background_color=rx.cond(DashboardState.is_live, style.COLOR_GREEN, "#f59e0b"),
                    width="10px",
                    height="10px",
                    border_radius="50%",
                    transition="all 0.3s ease",
                ),
                rx.text(
                    DashboardState.live_label,
                    size="2",
                    weight="bold",
                    color=DashboardState.live_color,
                    font_family=style.FONT_FAMILY_MONO,
                ),
                spacing="2",
                align="center",
            ),

            rx.divider(orientation="vertical", size="2", color="rgba(255,255,255,0.08)"),

            # Relógio
            rx.hstack(
                rx.icon("clock", size=14, color=style.COLOR_GRAY),
                rx.text(DashboardState.relogio, size="2", color=style.COLOR_TEXT, font_family=style.FONT_FAMILY_MONO),
                spacing="2",
                align="center",
            ),

            rx.divider(orientation="vertical", size="2", color="rgba(255,255,255,0.08)"),

            # Seletor de Intervalo
            rx.hstack(
                rx.text("Auto-refresh:", size="2", color=style.COLOR_GRAY),
                rx.select(
                    ["3", "5", "10", "30"],
                    default_value="5",
                    on_change=DashboardState.set_intervalo,
                    size="1",
                    variant="surface",
                    color_scheme="indigo",
                ),
                rx.text("s", size="2", color=style.COLOR_GRAY),
                spacing="2",
                align="center",
            ),

            rx.spacer(),

            # Botões de Ação
            rx.button(
                rx.icon("refresh-cw", size=14),
                "Atualizar Agora",
                on_click=DashboardState.atualizar_agora,
                variant="outline",
                size="1",
                radius="full",
                color_scheme="indigo",
                cursor="pointer",
            ),
            rx.button(
                rx.cond(
                    DashboardState.is_live,
                    rx.hstack(rx.icon("pause", size=14), rx.text("Pausar"), spacing="1"),
                    rx.hstack(rx.icon("play", size=14), rx.text("Retomar"), spacing="1"),
                ),
                on_click=DashboardState.toggle_live,
                variant=rx.cond(DashboardState.is_live, "solid", "outline"),
                color_scheme=rx.cond(DashboardState.is_live, "green", "amber"),
                size="1",
                radius="full",
                cursor="pointer",
            ),

            spacing="3",
            align="center",
            width="100%",
        ),
        width="100%",
        variant="classic",
        background_color=style.CARD_BG,
        border=f"1px solid {style.CARD_BORDER}",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.4)",
        padding_x="4",
        padding_y="3",
        border_radius="xl",
    )


# ─────────────────────────────────────────────
# LAYOUT COMPONENTES (SIDEBAR & CONTEÚDO)
# ─────────────────────────────────────────────

def sidebar_item(label: str, icon: str, active: bool = False) -> rx.Component:
    """Item individual da barra lateral com hover e active borders."""
    return rx.hstack(
        rx.icon(icon, color=style.COLOR_CYAN if active else style.COLOR_GRAY, size=16),
        rx.text(
            label,
            size="2",
            color=style.COLOR_TEXT if active else style.COLOR_GRAY,
            weight="medium" if active else "regular",
        ),
        background="rgba(255,255,255,0.02)" if active else "transparent",
        border_left=f"3px solid {style.COLOR_CYAN}" if active else "3px solid transparent",
        padding_y="2.5",
        padding_x="4",
        width="100%",
        cursor="pointer",
        align="center",
        spacing="3",
        _hover={
            "background_color": "rgba(255,255,255,0.02)",
            "color": style.COLOR_TEXT,
        },
        transition="all 0.2s ease",
    )


def sidebar() -> rx.Component:
    """Sidebar estruturada baseada no layout Nexus-OS."""
    return rx.vstack(
        # Brand Header
        rx.hstack(
            rx.icon("hexagon", color=style.COLOR_CYAN, size=22),
            rx.text("NEXUS OS", size="4", weight="bold", color=style.COLOR_TEXT, font_family=style.FONT_FAMILY_MONO),
            spacing="2",
            padding_y="6",
            padding_x="6",
            align="center",
            width="100%",
        ),
        
        # Search bar
        rx.box(
            rx.hstack(
                rx.icon("search", color=style.COLOR_GRAY, size=14),
                rx.text("Buscar sistemas...", size="2", color=style.COLOR_GRAY),
                spacing="2",
                align="center",
            ),
            border=f"1px solid {style.CARD_BORDER}",
            background="rgba(255,255,255,0.02)",
            padding_y="2",
            padding_x="3",
            margin_x="4",
            margin_bottom="6",
            border_radius="md",
            width="90%",
        ),

        # Navigation menu
        sidebar_item("Dashboard", "layout-dashboard", active=True),
        sidebar_item("Diagnostics", "activity"),
        sidebar_item("Data Center", "server"),
        sidebar_item("Network", "network"),
        sidebar_item("Security", "shield"),
        sidebar_item("Console", "terminal"),
        sidebar_item("Communications", "message-square"),
        sidebar_item("Settings", "settings"),

        rx.spacer(),

        # System Status Footer
        rx.vstack(
            rx.text("STATUS DO SISTEMA", size="1", color=style.COLOR_GRAY, weight="bold", letter_spacing="0.05em", padding_x="6"),
            
            # Core Systems status
            rx.vstack(
                rx.hstack(
                    rx.text("Core Systems", size="1", color=style.COLOR_GRAY),
                    rx.spacer(),
                    rx.text("89%", size="1", color=style.COLOR_CYAN, font_family=style.FONT_FAMILY_MONO),
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        width="89%",
                        height="4px",
                        background_color=style.COLOR_CYAN,
                        border_radius="full",
                    ),
                    width="100%",
                    height="4px",
                    background_color=style.CARD_BORDER,
                    border_radius="full",
                ),
                width="100%",
                padding_x="6",
                spacing="1",
            ),

            # Security status
            rx.vstack(
                rx.hstack(
                    rx.text("Security", size="1", color=style.COLOR_GRAY),
                    rx.spacer(),
                    rx.text("75%", size="1", color=style.COLOR_CYAN, font_family=style.FONT_FAMILY_MONO),
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        width="75%",
                        height="4px",
                        background_color=style.COLOR_CYAN,
                        border_radius="full",
                    ),
                    width="100%",
                    height="4px",
                    background_color=style.CARD_BORDER,
                    border_radius="full",
                ),
                width="100%",
                padding_x="6",
                spacing="1",
            ),

            # Network status
            rx.vstack(
                rx.hstack(
                    rx.text("Network", size="1", color=style.COLOR_GRAY),
                    rx.spacer(),
                    rx.text("86%", size="1", color=style.COLOR_CYAN, font_family=style.FONT_FAMILY_MONO),
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        width="86%",
                        height="4px",
                        background_color=style.COLOR_CYAN,
                        border_radius="full",
                    ),
                    width="100%",
                    height="4px",
                    background_color=style.CARD_BORDER,
                    border_radius="full",
                ),
                width="100%",
                padding_x="6",
                spacing="1",
            ),

            width="100%",
            spacing="3",
            padding_bottom="6",
        ),

        width=style.SIDEBAR_WIDTH,
        border_right=f"1px solid {style.CARD_BORDER}",
        background_color="#0b0c10",
        display=rx.breakpoints(initial="none", md="flex"),
        height="100vh",
        align_items="start",
    )


def conteudo_principal() -> rx.Component:
    """Conteúdo de métricas e tabelas principal à direita."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.icon("activity", color=style.COLOR_CYAN, size=20),
                        rx.heading("System Overview", size="6", color=style.COLOR_TEXT, font_family=style.FONT_FAMILY_MONO),
                        spacing="2",
                        align="center",
                    ),
                    rx.text("Hub de Inovação VIX · Nexus-OS Telemetry", size="2", color=style.COLOR_GRAY),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.badge(
                    "Motor: Antivravity Core v1.2",
                    variant="soft",
                    color_scheme="cyan",
                    size="2",
                    radius="full",
                    padding_x="3",
                    padding_y="1",
                ),
                width="100%",
                align="center",
                padding_bottom="2",
            ),

            # Controles de tempo real
            controles_live(),

            # Grid de KPIs
            rx.grid(
                kpi_card(
                    "ROI Líquido Total",
                    DashboardState.kpi_roi_fmt,
                    "trending-up",
                    style.COLOR_GREEN,
                    f"4px solid {style.COLOR_GREEN}",
                    DashboardState.roi_history,
                    trend_icon=DashboardState.roi_trend_icon,
                    trend_color=DashboardState.roi_trend_color,
                ),
                kpi_card(
                    "Horas Recuperadas",
                    rx.text(DashboardState.kpi_horas, "h"),
                    "clock",
                    style.COLOR_CYAN,
                    f"4px solid {style.COLOR_CYAN}",
                    DashboardState.horas_history,
                    trend_icon=DashboardState.horas_trend_icon,
                    trend_color=DashboardState.horas_trend_color,
                ),
                kpi_card(
                    "Governança Média",
                    rx.text(DashboardState.kpi_governanca, "%"),
                    "shield-check",
                    style.COLOR_ROSE,
                    f"4px solid {style.COLOR_ROSE}",
                    DashboardState.governanca_history,
                    trend_icon=DashboardState.governanca_trend_icon,
                    trend_color=DashboardState.governanca_trend_color,
                ),
                kpi_card(
                    "Total de Iniciativas",
                    DashboardState.kpi_total,
                    "layers",
                    style.COLOR_PURPLE,
                    f"4px solid {style.COLOR_PURPLE}",
                    DashboardState.total_history,
                    trend_icon="",
                    trend_color="",
                ),
                columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                spacing="4",
                width="100%",
            ),

            # Gráficos (Performance e Distribuição)
            rx.flex(
                rx.box(
                    performance_chart_card(),
                    width=rx.breakpoints(initial="100%", lg="65%"),
                ),
                rx.box(
                    donut_chart_card(),
                    width=rx.breakpoints(initial="100%", lg="35%"),
                ),
                spacing="4",
                width="100%",
                flex_direction=rx.breakpoints(initial="column", lg="row"),
            ),

            # Tabela de Governança
            rx.vstack(
                rx.hstack(
                    rx.heading("Status de Governança", size="5", color=style.COLOR_TEXT, weight="bold"),
                    rx.spacer(),
                    filtros_area(),
                    width="100%",
                    align="center",
                ),
                rx.card(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Iniciativa", color=style.COLOR_GRAY),
                                rx.table.column_header_cell("Área", color=style.COLOR_GRAY),
                                rx.table.column_header_cell("Responsável", color=style.COLOR_GRAY),
                                rx.table.column_header_cell("Status", color=style.COLOR_GRAY),
                                rx.table.column_header_cell("Prioridade", color=style.COLOR_GRAY),
                                rx.table.column_header_cell("ROI Estimado", color=style.COLOR_GRAY),
                                rx.table.column_header_cell("Indicador", color=style.COLOR_GRAY),
                                align="center",
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(DashboardState.iniciativas, linha_iniciativa),
                            css={"& tr:nth-of-type(odd)": {"background": "rgba(255, 255, 255, 0.015)"}},
                        ),
                        width="100%",
                        variant="ghost",
                    ),
                    width="100%",
                    padding="0",
                    background_color=style.CARD_BG,
                    border=f"1px solid {style.CARD_BORDER}",
                    box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.4)",
                    border_radius="xl",
                    overflow="hidden",
                ),
                width="100%",
                spacing="4",
                margin_top="4",
            ),

            spacing="6",
            width="100%",
        ),
        flex="1",
        padding="6",
        overflow_y="auto",
        height="100vh",
    )


# ─────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ─────────────────────────────────────────────

def index() -> rx.Component:
    return rx.box(
        # CSS injetado para animação pulsante
        rx.html(
            """
            <style>
            @keyframes pulse {
              0% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
              }
              70% {
                transform: scale(1);
                box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
              }
              100% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
              }
            }
            .pulse-dot {
              animation: pulse 2s infinite;
            }
            </style>
            """
        ),
        rx.flex(
            sidebar(),
            conteudo_principal(),
            width="100%",
            min_height="100vh",
            background_color=style.BG_COLOR,
        ),
        width="100%",
        min_height="100vh",
        background_color=style.BG_COLOR,
    )


# ─────────────────────────────────────────────
# APP DEPLOY
# ─────────────────────────────────────────────

app = rx.App()
app.add_page(
    index,
    title="Hub de Inovação VIX | Nexus-OS",
    description="Painel estratégico de governança e análise de portfólio corporativo.",
    on_load=DashboardState.iniciar_live,
)
