"""
style.py — Nexus-OS Style Design Tokens & Global Configuration
Defines colors, dimensions, borders, and styles matching the high-contrast dashboard.
"""

# ─────────────────────────────────────────────
# PALETA DE CORES (NEXUS-OS STYLE)
# ─────────────────────────────────────────────

BG_COLOR = "#050608"          # Preto profundo do Nexus-OS
CARD_BG = "#0f1115"           # Fundo escuro dos cards
CARD_BORDER = "#1e2129"       # Borda escura suave

# Destaques em Ciano e Roxo (Gradiente Nexus)
COLOR_CYAN = "#06b6d4"        # Ciano elétrico
COLOR_PURPLE = "#8b5cf6"      # Roxo profundo
COLOR_ROSE = "#f43f5e"        # Rosa para alertas/governança
COLOR_GRAY = "#94a3b8"        # Cinza para rótulos/labels
COLOR_TEXT = "#f8fafc"        # Texto claro
COLOR_GREEN = "#10b981"       # Verde esmeralda (KPI ROI / Sucesso)

# Gradiente Nexus
GRADIENT_NEXUS = "linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%)"

# ─────────────────────────────────────────────
# FONTES & TIPOGRAFIA
# ─────────────────────────────────────────────

FONT_FAMILY_MONO = "'SF Mono', Fira Code, 'Courier New', Courier, monospace"
FONT_FAMILY_SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

# ─────────────────────────────────────────────
# ELEMENTOS E CLASSES REUTILIZÁVEIS
# ─────────────────────────────────────────────

NEXUS_CARD_STYLE = {
    "background_color": CARD_BG,
    "border": f"1px solid {CARD_BORDER}",
    "border_radius": "lg",
    "box_shadow": "0 4px 20px 0 rgba(0, 0, 0, 0.5)",
    "padding": "5",
    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "border_color": "#06b6d4aa",
        "box_shadow": "0 8px 30px 0 rgba(6, 182, 212, 0.15)",
    }
}

SIDEBAR_WIDTH = "240px"
