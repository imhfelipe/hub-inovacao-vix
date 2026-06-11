"""
hub_vix.py — Interface Reativa do Hub de Inovação VIX
Dashboard em tempo real com background task de alto desempenho.
Refatorado para Design SaaS Premium de nível "Data Intelligence" (Glassmorphism, Recharts Donut, micro-tendências e tabela otimizada).
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
        return rx.cond(curr > prev, "#10b981", rx.cond(curr < prev, "#f43f5e", "#64748b"))

    @rx.var
    def horas_trend_icon(self) -> rx.Var:
        curr = self.horas_atual
        prev = self.prev_horas
        return rx.cond(curr > prev, "arrow-up-right", rx.cond(curr < prev, "arrow-down-right", "minus"))

    @rx.var
    def horas_trend_color(self) -> rx.Var:
        curr = self.horas_atual
        prev = self.prev_horas
        return rx.cond(curr > prev, "#10b981", rx.cond(curr < prev, "#f43f5e", "#64748b"))

    @rx.var
    def governanca_trend_icon(self) -> rx.Var:
        curr = self.governanca_atual
        prev = self.prev_governanca
        return rx.cond(curr > prev, "arrow-up-right", rx.cond(curr < prev, "arrow-down-right", "minus"))

    @rx.var
    def governanca_trend_color(self) -> rx.Var:
        curr = self.governanca_atual
        prev = self.prev_governanca
        return rx.cond(curr > prev, "#10b981", rx.cond(curr < prev, "#f43f5e", "#64748b"))

    @rx.var
    def live_label(self) -> str:
        return "● AO VIVO" if self.is_live else "⏸ PAUSADO"

    @rx.var
    def live_color(self) -> str:
        return "#10b981" if self.is_live else "#f59e0b"

    # ── Background: loop de tempo real ────────

    def guardar_historico(self):
        """Salva a leitura de KPIs anterior para calcular tendências antes de puxar dados novos."""
        k = calcular_kpis(self.iniciativas)
        self.prev_roi = float(k.get("roi", 0.0))
        self.prev_horas = float(k.get("horas", 0))
        self.prev_governanca = float(k.get("governanca", 0.0))

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


# ─────────────────────────────────────────────
# COMPONENTES PREMIUM DESIGN SYSTEM (GLASSMORPHISM)
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
                color_scheme="indigo",
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


def kpi_card(label: str, valor, icon: str, cor: str, border_left: str, trend_icon: str = "", trend_color: str = "") -> rx.Component:
    """Card de KPI com Glassmorphism, borda lateral colorida, glow no texto e micro-indicador de tendência."""
    return rx.card(
        rx.vstack(
            # Título e ícone superior
            rx.hstack(
                rx.icon(icon, color=cor, size=18),
                rx.text(label, size="1", color="#94a3b8", weight="medium"),
                justify="start",
                width="100%",
                align="center",
            ),
            # Valor e micro-tendência
            rx.hstack(
                rx.text(
                    valor,
                    size="8",
                    weight="bold",
                    color=cor,
                    margin_top="2",
                    text_shadow=f"0 0 20px {cor}3b",  # Brilho text-shadow sutil
                ),
                rx.cond(
                    trend_icon != "",
                    rx.box(
                        rx.cond(
                            trend_icon == "arrow-up-right",
                            rx.icon("arrow-up-right", color=trend_color, size=18),
                            rx.cond(
                                trend_icon == "arrow-down-right",
                                rx.icon("arrow-down-right", color=trend_color, size=18),
                                rx.icon("minus", color=trend_color, size=18)
                            )
                        ),
                        margin_top="3",
                        margin_left="1",
                    ),
                ),
                align="center",
                width="100%",
            ),
            spacing="1",
            align="start",
        ),
        width="100%",
        variant="classic",
        background="rgba(255, 255, 255, 0.03)",  # Glassmorphism (opacidade super baixa)
        backdrop_filter="blur(16px)",             # Blur de fundo
        border="1px solid rgba(255, 255, 255, 0.08)",
        border_left=border_left,                  # Borda esquerda colorida e chamativa
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": f"0 12px 24px -10px rgba(0,0,0,0.5), 0 0 16px {cor}25",
            "border_color": f"{cor}60",
        },
        padding="5",
        border_radius="xl",
    )


def donut_chart_card() -> rx.Component:
    """Card de Gráfico Donut de Status (Glassmorphism)."""
    return rx.card(
        rx.vstack(
            rx.text("Distribuição por Status", size="2", color="#94a3b8", weight="medium"),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    rx.recharts.cell(fill="#10b981"),  # Concluídas - Emerald
                    rx.recharts.cell(fill="#3b82f6"),  # Em Andamento - Blue
                    rx.recharts.cell(fill="#f59e0b"),  # Planejadas - Orange
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
        background="rgba(255, 255, 255, 0.03)",  # Glassmorphism (opacidade super baixa)
        backdrop_filter="blur(16px)",
        border="1px solid rgba(255, 255, 255, 0.08)",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.37)",
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
            rx.text(iniciativa["responsavel"], size="2", color="#94a3b8")
        ),
        rx.table.cell(badge_status(iniciativa["status"])),
        rx.table.cell(badge_prioridade(iniciativa["prioridade"])),
        rx.table.cell(
            rx.text(
                iniciativa["roi_fmt"],
                weight="bold",
                size="2",
                color=rx.cond(iniciativa["roi"] > 0, "#10b981", "#94a3b8"),  # Emerald-500
            ),
        ),
        rx.table.cell(
            rx.cond(
                iniciativa["tem_indicador"],
                rx.icon("circle-check", color="#10b981", size=18),
                rx.icon("circle-alert", color="#f43f5e", size=18),
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
                    "linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%)",
                    "transparent"
                ),
                border=rx.cond(
                    DashboardState.area_selecionada == area,
                    "none",
                    "1px solid rgba(255, 255, 255, 0.15)"
                ),
                color=rx.cond(DashboardState.area_selecionada == area, "#ffffff", "#94a3b8"),
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
                    width="8px",
                    height="8px",
                    border_radius="50%",
                    background_color=DashboardState.live_color,
                    box_shadow=rx.cond(
                        DashboardState.is_live,
                        "0 0 10px #10b981",
                        "none",
                    ),
                    transition="all 0.3s ease",
                ),
                rx.text(
                    DashboardState.live_label,
                    size="2",
                    weight="bold",
                    color=DashboardState.live_color,
                ),
                spacing="2",
                align="center",
            ),

            rx.divider(orientation="vertical", size="2", color="rgba(255,255,255,0.08)"),

            # Relógio
            rx.hstack(
                rx.icon("clock", size=14, color="#64748b"),
                rx.text(DashboardState.relogio, size="2", color="#94a3b8", font_family="monospace"),
                spacing="2",
                align="center",
            ),

            rx.divider(orientation="vertical", size="2", color="rgba(255,255,255,0.08)"),

            # Seletor de Intervalo
            rx.hstack(
                rx.text("Auto-refresh:", size="2", color="#64748b"),
                rx.select(
                    ["3", "5", "10", "30"],
                    default_value="5",
                    on_change=DashboardState.set_intervalo,
                    size="1",
                    variant="surface",
                    color_scheme="indigo",
                ),
                rx.text("s", size="2", color="#64748b"),
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
        background="rgba(255, 255, 255, 0.03)",  # Glassmorphism (opacidade super baixa)
        backdrop_filter="blur(16px)",
        border="1px solid rgba(255, 255, 255, 0.08)",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        padding_x="4",
        padding_y="3",
        border_radius="xl",
    )


# ─────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ─────────────────────────────────────────────

def index() -> rx.Component:
    return rx.box(
        rx.container(
            rx.vstack(

                # ── Cabeçalho SaaS ──────────────────────────
                rx.hstack(
                    rx.vstack(
                        rx.heading("Hub de Inovação VIX", size="7", weight="bold", color="#f8fafc"),
                        rx.text(
                            "Painel Estratégico de Governança · Portfólio de Iniciativas",
                            size="3",
                            color="#94a3b8",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.badge(
                        "Motor: Antivravity Core v1.1",
                        variant="soft",
                        color_scheme="indigo",
                        size="2",
                        radius="full",
                        padding_x="3",
                        padding_y="1",
                    ),
                    width="100%",
                    align="center",
                    padding_bottom="2",
                ),

                # ── Controles Live ─────────────────────────
                controles_live(),

                # ── KPIs e Gráfico de Distribuição Status ───
                rx.flex(
                    # Grid de KPIs à esquerda (65% width no md)
                    rx.box(
                        rx.grid(
                            kpi_card(
                                "ROI Líquido Total",
                                DashboardState.kpi_roi_fmt,
                                "trending-up",
                                "#10b981",  # Emerald
                                "4px solid #10b981",
                                trend_icon=DashboardState.roi_trend_icon,
                                trend_color=DashboardState.roi_trend_color,
                            ),
                            kpi_card(
                                "Horas Recuperadas",
                                rx.text(DashboardState.kpi_horas, "h"),
                                "clock",
                                "#3b82f6",  # Cobalt Blue
                                "4px solid #3b82f6",
                                trend_icon=DashboardState.horas_trend_icon,
                                trend_color=DashboardState.horas_trend_color,
                            ),
                            kpi_card(
                                "Governança Média",
                                rx.text(DashboardState.kpi_governanca, "%"),
                                "shield-check",
                                "#f43f5e",  # Rose
                                "4px solid #f43f5e",
                                trend_icon=DashboardState.governanca_trend_icon,
                                trend_color=DashboardState.governanca_trend_color,
                            ),
                            kpi_card(
                                "Total de Iniciativas",
                                DashboardState.kpi_total,
                                "layers",
                                "#6366f1",  # Indigo
                                "4px solid #6366f1",
                                trend_icon="",
                                trend_color="",
                            ),
                            columns=rx.breakpoints(initial="1", sm="2"),
                            spacing="4",
                            width="100%",
                        ),
                        width=rx.breakpoints(initial="100%", md="65%"),
                    ),
                    # Donut Chart à direita (35% width no md)
                    rx.box(
                        donut_chart_card(),
                        width=rx.breakpoints(initial="100%", md="35%"),
                    ),
                    spacing="4",
                    width="100%",
                    flex_direction=rx.breakpoints(initial="column", md="row"),
                ),

                # ── Grid/Tabela de Governança ───────────────
                rx.vstack(
                    rx.hstack(
                        rx.heading("Status de Governança", size="5", color="#f8fafc", weight="bold"),
                        rx.spacer(),
                        filtros_area(),
                        width="100%",
                        align="center",
                    ),
                    rx.card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Iniciativa", color="#94a3b8"),
                                    rx.table.column_header_cell("Área", color="#94a3b8"),
                                    rx.table.column_header_cell("Responsável", color="#94a3b8"),
                                    rx.table.column_header_cell("Status", color="#94a3b8"),
                                    rx.table.column_header_cell("Prioridade", color="#94a3b8"),
                                    rx.table.column_header_cell("ROI Estimado", color="#94a3b8"),
                                    rx.table.column_header_cell("Indicador", color="#94a3b8"),
                                    align="center",
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(DashboardState.iniciativas, linha_iniciativa),
                                css={"& tr:nth-of-type(odd)": {"background": "rgba(255, 255, 255, 0.015)"}},  # Alternar linhas
                            ),
                            width="100%",
                            variant="ghost",  # Remove linhas verticais
                        ),
                        width="100%",
                        padding="0",
                        background="rgba(255, 255, 255, 0.03)",  # Glassmorphism (opacidade super baixa)
                        backdrop_filter="blur(16px)",
                        border="1px solid rgba(255, 255, 255, 0.08)",
                        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.37)",
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
            max_width="1200px",
            padding_x="6",
            padding_y="8",
            margin_x="auto",
        ),
        min_height="100vh",
        background_color="#020617",  # Slate-950
    )


# ─────────────────────────────────────────────
# APP DEPLOY
# ─────────────────────────────────────────────

app = rx.App()
app.add_page(
    index,
    title="Hub de Inovação VIX | Dashboard SaaS",
    description="Painel estratégico de governança e análise de portfólio corporativo.",
    on_load=DashboardState.iniciar_live,  # inicia o loop ao abrir a página
)
