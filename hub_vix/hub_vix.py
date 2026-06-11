"""
hub_vix.py — Interface Reativa do Hub de Inovação VIX
Dashboard em tempo real com background task de alto desempenho.
Redesenhado para Visual SaaS Premium de nível corporativo.
"""

import asyncio
from typing import TypedDict
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


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────

class DashboardState(rx.State):
    """Estado global com atualização em tempo real via background task."""

    iniciativas_raw: list[Iniciativa] = get_dados_iniciativas()
    area_selecionada: str = "Todas"

    # Controles de tempo real
    is_live: bool = True
    intervalo_seg: int = 5
    relogio: str = datetime.now().strftime("%H:%M:%S")
    tick: int = 0  # contador de ticks

    # ── Vars derivadas ────────────────────────

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

    @rx.var
    def kpi_em_andamento(self) -> int:
        return calcular_kpis(self.iniciativas).get("em_andamento", 0)

    @rx.var
    def kpi_concluidas(self) -> int:
        return calcular_kpis(self.iniciativas).get("concluidas", 0)

    @rx.var
    def kpi_planejadas(self) -> int:
        k = calcular_kpis(self.iniciativas)
        return k.get("total", 0) - k.get("em_andamento", 0) - k.get("concluidas", 0)

    @rx.var
    def live_label(self) -> str:
        return "● AO VIVO" if self.is_live else "⏸ PAUSADO"

    @rx.var
    def live_color(self) -> str:
        return "#10b981" if self.is_live else "#f59e0b"

    # ── Background: loop de tempo real ────────

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
        self.iniciativas_raw = get_dados_realtime()


# ─────────────────────────────────────────────
# COMPONENTES PREMIUM DESIGN SYSTEM
# ─────────────────────────────────────────────

def badge_status(status: str) -> rx.Component:
    """Badge elegante de status arredondado."""
    return rx.badge(
        status,
        color_scheme=rx.cond(
            status == "Concluída", "green",
            rx.cond(status == "Em Andamento", "indigo", "orange")
        ),
        variant="soft",
        radius="full",
        padding_x="3",
        padding_y="1",
        weight="medium",
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


def kpi_card(label: str, valor, icon: str, cor: str) -> rx.Component:
    """Card de KPI premium com gradiente de borda sutil e hover interativo."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, color=cor, size=18),
                rx.text(label, size="1", color="#94a3b8", weight="medium"),
                justify="start",
                width="100%",
                align="center",
            ),
            rx.text(
                valor,
                size="8",
                weight="bold",
                color=cor,
                margin_top="2",
            ),
            spacing="1",
            align="start",
        ),
        width="100%",
        variant="classic",
        background_color="#0f172a",  # Slate-900
        border="1px solid rgba(99, 102, 241, 0.12)",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": f"0 12px 24px -10px rgba(0,0,0,0.4), 0 0 16px {cor}1a",
            "border_color": f"{cor}60",
        },
        padding="5",
        border_radius="xl",
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
                formatar_roi(iniciativa["roi"]),
                weight="bold",
                size="2",
                color=rx.cond(iniciativa["roi"] > 0, "#10b981", "#94a3b8"),  # Emerald-500
            ),
        ),
        rx.table.cell(
            rx.icon(
                rx.cond(iniciativa["tem_indicador"], "check-circle", "alert-circle"),
                color=rx.cond(iniciativa["tem_indicador"], "#10b981", "#f43f5e"),  # Emerald-500 / Rose-500
                size=18,
            ),
        ),
        align="center",
        _hover={"background_color": "rgba(255, 255, 255, 0.015)"},
        transition="background-color 0.2s ease",
    )


def filtros_area() -> rx.Component:
    """Selector de áreas estéreo com botões de capsula."""
    return rx.hstack(
        rx.foreach(
            DashboardState.areas,
            lambda area: rx.button(
                area,
                on_click=DashboardState.selecionar_area(area),
                variant=rx.cond(DashboardState.area_selecionada == area, "solid", "outline"),
                radius="full",
                size="2",
                color_scheme="indigo",
                cursor="pointer",
            ),
        ),
        spacing="2",
        wrap="wrap",
    )


def controles_live() -> rx.Component:
    """Barra de controle em tempo real do estilo SaaS."""
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

            rx.divider(orientation="vertical", size="2", color="rgba(255,255,255,0.05)"),

            # Relógio
            rx.hstack(
                rx.icon("clock", size=14, color="#64748b"),
                rx.text(DashboardState.relogio, size="2", color="#94a3b8", font_family="monospace"),
                spacing="2",
                align="center",
            ),

            rx.divider(orientation="vertical", size="2", color="rgba(255,255,255,0.05)"),

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
        background_color="#0f172a",  # Slate-900
        border="1px solid rgba(255,255,255,0.04)",
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

                # ── Grid de KPIs ───────────────────────────
                rx.grid(
                    kpi_card(
                        "ROI Líquido Total",
                        DashboardState.kpi_roi_fmt,
                        "trending-up",
                        "#10b981",  # Emerald-500 para indicadores positivos
                    ),
                    kpi_card(
                        "Horas Recuperadas",
                        rx.text(DashboardState.kpi_horas, "h"),
                        "clock",
                        "#3b82f6",  # Cobalt Blue
                    ),
                    kpi_card(
                        "Governança Média",
                        rx.text(DashboardState.kpi_governanca, "%"),
                        "shield-check",
                        "#f43f5e",  # Rose-500 para governança
                    ),
                    kpi_card(
                        "Total de Iniciativas",
                        DashboardState.kpi_total,
                        "layers",
                        "#6366f1",  # Indigo
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                    margin_top="2",
                ),

                # ── Sub-dashboard de status ─────────────────
                rx.card(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Em Andamento", size="2", color="#94a3b8", weight="medium"),
                            rx.text(
                                DashboardState.kpi_em_andamento,
                                size="7", weight="bold", color="#3b82f6",
                            ),
                            align="center",
                            width="100%",
                        ),
                        rx.divider(orientation="vertical", size="3", color="rgba(255,255,255,0.05)"),
                        rx.vstack(
                            rx.text("Concluídas", size="2", color="#94a3b8", weight="medium"),
                            rx.text(
                                DashboardState.kpi_concluidas,
                                size="7", weight="bold", color="#10b981",
                            ),
                            align="center",
                            width="100%",
                        ),
                        rx.divider(orientation="vertical", size="3", color="rgba(255,255,255,0.05)"),
                        rx.vstack(
                            rx.text("Planejadas", size="2", color="#94a3b8", weight="medium"),
                            rx.text(
                                DashboardState.kpi_planejadas,
                                size="7", weight="bold", color="#f59e0b",
                            ),
                            align="center",
                            width="100%",
                        ),
                        spacing="6",
                        justify="center",
                        width="100%",
                        align="center",
                    ),
                    width="100%",
                    variant="classic",
                    background_color="#0f172a",  # Slate-900
                    border="1px solid rgba(255,255,255,0.04)",
                    padding="4",
                    border_radius="xl",
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
                            ),
                            width="100%",
                            variant="surface",
                        ),
                        width="100%",
                        padding="0",
                        border="1px solid rgba(255,255,255,0.04)",
                        background_color="#0f172a",  # Slate-900
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
