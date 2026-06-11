# Hub de Inovação VIX 🚀

Este dashboard utiliza uma interface inspirada em sistemas de monitoramento de alta disponibilidade (Nexus-OS), focada em reduzir a carga cognitiva da diretoria através de elementos visuais de alto contraste e indicadores em tempo real.

Painel estratégico de governança de projetos em tempo real.  
Arquitetura modular e de alta performance de nível **SaaS Premium**: **Antivravity Core** (motor Python baseado em Dataclasses) + **Reflex** (interface reativa e moderna baseada em Radix Themes).

## ▶ Rodar localmente

Certifique-se de que o Python esteja instalado e execute os seguintes comandos na raiz do projeto:

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar e rodar o servidor do Reflex
reflex run
```

O aplicativo estará disponível em:
- Frontend: `http://localhost:3000` (ou a porta subsequente disponível, como `:3003`)
- Backend/API: `http://localhost:8000` (ou a porta subsequente disponível)

## 📁 Estrutura do Projeto

```
├── hub_vix/
│   ├── __init__.py
│   ├── hub_vix.py           # Interface reativa do Dashboard em Reflex (Radix UI)
│   ├── antivravity_core.py  # Motor de Inteligência e processamento de KPIs (Dataclasses)
├── rxconfig.py              # Arquivo de configuração do Reflex
├── requirements.txt         # Dependências do projeto (Reflex, Pandas)
└── README.md
```

## ⚙️ Funcionalidades em Tempo Real & Design System

O painel é reativo e atualiza seus dados de forma assíncrona usando o recurso de **background tasks** do Reflex:
- **Relógio e Refresh:** Sincronizado a cada 1 segundo no frontend.
- **Modo Ao Vivo:** Simulação em tempo real (variação de ±3% de ROI, ±2h de esforço e chance de mudança de status de projetos a cada ciclo).
- **Design System SaaS:** Fundo escuro em tom slate-950, cartões de KPI integrados no slate-900 com gradientes nas bordas, sombras suaves, efeitos dinâmicos de hover e badges de prioridade/status baseadas em cores corporativas (Emerald-500 para positivo, Rose-500 para governança pendente).
