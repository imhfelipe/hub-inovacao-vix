# Hub de Inovação VIX 🚀

Painel estratégico de governança de projetos em tempo real.  
Arquitetura modular: **Antivravity** (motor Python) + **Streamlit** (interface reativa).

## ▶ Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Deploy no Streamlit Community Cloud (grátis)

1. Suba este repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Clique em **"New app"**
4. Selecione o repositório e o arquivo `app.py`
5. Clique em **Deploy** — pronto! URL pública gerada automaticamente

## 📁 Estrutura

```
├── app.py           # Interface Streamlit (frontend reativo)
├── antivravity.py   # Motor de KPIs (backend de inteligência)
├── requirements.txt # Dependências
└── README.md
```

## ⚙️ Como funciona o tempo real

O dashboard usa `st.rerun()` com `time.sleep(1)` para atualizar automaticamente.  
O motor `antivravity.py` simula variações de dados a cada ciclo (±3% ROI, ±2h).

Controles disponíveis na sidebar:
- 🔴 **Modo Ao Vivo** — ativa/pausa o auto-refresh
- ⏱ **Intervalo** — 3 / 5 / 10 / 30 / 60 segundos
- 🏢 **Filtro por Área** — TI, Infra, RH, Comercial
- 🔄 **Atualizar Agora** — refresh manual imediato
