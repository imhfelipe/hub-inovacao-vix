"""
app.py — Hub de Inovação VIX
Interface Streamlit com atualização em tempo real via st.rerun().
Motor: antivravity.py
"""

import time
from datetime import datetime
import streamlit as st
from antivravity import (
    calcular_kpis,
    get_dados_realtime,
    get_dados_iniciativas,
    filtrar_por_area,
    get_areas_disponiveis,
    formatar_roi,
)

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Hub de Inovação VIX | Painel de Governança",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS GLOBAIS (CSS PREMIUM DARK)
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Fundo geral */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 50%, #0a0f1a 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 15, 30, 0.95) !important;
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}

/* Cards de métricas */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 16px;
    padding: 1.2rem 1.5rem !important;
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(139, 92, 246, 0.08);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(139, 92, 246, 0.15);
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #e2e8f0 !important;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Título principal */
h1 { 
    color: #f1f5f9 !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}
h2, h3 { color: #e2e8f0 !important; font-weight: 700 !important; }

/* Tabela */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
thead tr th {
    background: rgba(139, 92, 246, 0.15) !important;
    color: #c4b5fd !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em;
}

/* Botões */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* Toggle */
.stToggle { color: #94a3b8 !important; }

/* Divisor */
hr { border-color: rgba(139, 92, 246, 0.2) !important; }

/* Texto padrão */
p, li, label { color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE (persiste entre reruns)
# ─────────────────────────────────────────────

if "iniciativas" not in st.session_state:
    st.session_state.iniciativas = get_dados_iniciativas()

if "is_live" not in st.session_state:
    st.session_state.is_live = True

if "intervalo" not in st.session_state:
    st.session_state.intervalo = 5

if "ultimo_refresh" not in st.session_state:
    st.session_state.ultimo_refresh = time.time()


# ─────────────────────────────────────────────
# SIDEBAR — CONTROLES
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Controles")
    st.markdown("---")

    # Toggle ao vivo
    is_live = st.toggle("🔴 Modo Ao Vivo", value=st.session_state.is_live)
    st.session_state.is_live = is_live

    # Intervalo
    intervalo = st.select_slider(
        "⏱ Intervalo (seg)",
        options=[3, 5, 10, 30, 60],
        value=st.session_state.intervalo,
    )
    st.session_state.intervalo = intervalo

    st.markdown("---")

    # Área de filtro
    areas = get_areas_disponiveis(st.session_state.iniciativas)
    area_selecionada = st.selectbox("🏢 Filtrar por Área", areas)

    st.markdown("---")

    # Botão de refresh manual
    if st.button("🔄 Atualizar Agora", use_container_width=True):
        st.session_state.iniciativas = get_dados_realtime()
        st.session_state.ultimo_refresh = time.time()

    st.markdown("---")
    st.markdown(
        "<small style='color:#6b7280'>Motor: **Antivravity v1.0**<br>"
        "Arquitetura modular · Dados reativos</small>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# ATUALIZAÇÃO EM TEMPO REAL
# ─────────────────────────────────────────────

agora = time.time()
if st.session_state.is_live and (agora - st.session_state.ultimo_refresh) >= st.session_state.intervalo:
    st.session_state.iniciativas = get_dados_realtime()
    st.session_state.ultimo_refresh = agora


# ─────────────────────────────────────────────
# DADOS PROCESSADOS
# ─────────────────────────────────────────────

iniciativas_filtradas = filtrar_por_area(st.session_state.iniciativas, area_selecionada)
kpis = calcular_kpis(iniciativas_filtradas)
ts = datetime.now().strftime("%H:%M:%S")


# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────

col_title, col_status = st.columns([3, 1])

with col_title:
    st.markdown("# 🚀 Hub de Inovação VIX")
    st.markdown(
        "<p style='color:#6b7280;margin-top:-12px'>Painel Estratégico de Governança · Portfólio de Iniciativas</p>",
        unsafe_allow_html=True,
    )

with col_status:
    if st.session_state.is_live:
        st.markdown(
            f"""<div style='
                background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.4);
                border-radius:12px;padding:12px 16px;text-align:center;margin-top:8px'>
                <span style='color:#10b981;font-size:1.1rem;font-weight:700'>● AO VIVO</span><br>
                <span style='color:#94a3b8;font-size:0.8rem;font-family:monospace'>{ts}</span><br>
                <span style='color:#6b7280;font-size:0.7rem'>Refresh: {st.session_state.intervalo}s</span>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div style='
                background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.4);
                border-radius:12px;padding:12px 16px;text-align:center;margin-top:8px'>
                <span style='color:#f59e0b;font-size:1.1rem;font-weight:700'>⏸ PAUSADO</span><br>
                <span style='color:#94a3b8;font-size:0.8rem;font-family:monospace'>{ts}</span>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("---")


# ─────────────────────────────────────────────
# KPIs PRINCIPAIS
# ─────────────────────────────────────────────

st.markdown("### 📊 Indicadores de Performance")
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        label="💰 ROI Líquido Total",
        value=formatar_roi(kpis["roi"]),
    )
with k2:
    st.metric(
        label="⏱ Horas Recuperadas",
        value=f"{kpis['horas']}h",
    )
with k3:
    st.metric(
        label="🛡 Governança",
        value=f"{kpis['governanca']}%",
    )
with k4:
    st.metric(
        label="📁 Total de Iniciativas",
        value=kpis["total"],
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PIPELINE DE STATUS
# ─────────────────────────────────────────────

st.markdown("### 🔁 Pipeline de Projetos")
p1, p2, p3 = st.columns(3)

planejadas = kpis["total"] - kpis["em_andamento"] - kpis["concluidas"]

with p1:
    st.markdown(
        f"""<div style='background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);
        border-radius:16px;padding:1.5rem;text-align:center'>
        <div style='color:#3b82f6;font-size:3rem;font-weight:800'>{kpis['em_andamento']}</div>
        <div style='color:#94a3b8;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.1em'>Em Andamento</div>
        </div>""",
        unsafe_allow_html=True,
    )
with p2:
    st.markdown(
        f"""<div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
        border-radius:16px;padding:1.5rem;text-align:center'>
        <div style='color:#10b981;font-size:3rem;font-weight:800'>{kpis['concluidas']}</div>
        <div style='color:#94a3b8;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.1em'>Concluídas</div>
        </div>""",
        unsafe_allow_html=True,
    )
with p3:
    st.markdown(
        f"""<div style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);
        border-radius:16px;padding:1.5rem;text-align:center'>
        <div style='color:#f59e0b;font-size:3rem;font-weight:800'>{planejadas}</div>
        <div style='color:#94a3b8;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.1em'>Planejadas</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABELA DE GOVERNANÇA
# ─────────────────────────────────────────────

st.markdown(f"### 📋 Status de Governança — {area_selecionada}")

# Formata tabela para exibição
import pandas as pd

df = pd.DataFrame(iniciativas_filtradas)
df_display = df[[
    "nome", "area", "responsavel", "status", "prioridade", "roi", "indicador_definido"
]].copy()

df_display.columns = [
    "Iniciativa", "Área", "Responsável", "Status", "Prioridade", "ROI (R$)", "Indicador ✓"
]
df_display["ROI (R$)"] = df_display["ROI (R$)"].apply(formatar_roi)
df_display["Indicador ✓"] = df_display["Indicador ✓"].apply(lambda x: "✅" if x else "❌")

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.TextColumn(width="medium"),
        "Prioridade": st.column_config.TextColumn(width="small"),
    },
)

st.markdown(
    f"<p style='color:#4b5563;font-size:0.75rem;text-align:right'>"
    f"Última atualização: {kpis['atualizado_em']} · Motor: Antivravity v1.0</p>",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# LOOP DE TEMPO REAL (st.rerun)
# ─────────────────────────────────────────────

if st.session_state.is_live:
    time.sleep(1)      # aguarda 1 segundo antes de cada rerun
    st.rerun()
