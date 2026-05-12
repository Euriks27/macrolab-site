import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from macrolab.dynamics import simulate_debt_trajectory
from macrolab.data_fetch import get_ipea_robust
from macrolab import load_brazil_data, run_spj, estimate_var_vecm

# Page config
st.set_page_config(
    page_title='MacroLab v7 - Análise Macroeconômica',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title('⚙️ Configurações')
page = st.sidebar.radio('Selecione a Página:', 
    ['🏠 Dashboard Principal', '📈 Simulações', '📊 Dados Históricos', '⚙️ Sobre'])

st.sidebar.markdown('---')
st.sidebar.info(
    'MacroLab v7\n\n'
    'Framework de Inteligência Macroeconômica\n\n'
    'Análise de Sustentabilidade Fiscal e Risco Soberano'
)

# ============================================================================
# PAGE 1: DASHBOARD PRINCIPAL
# ============================================================================
if page == '🏠 Dashboard Principal':
    st.markdown("<h1 class='main-header'>📊 Dashboard MacroLab v7</h1>", unsafe_allow_html=True)
    st.write('Framework modular de inteligência preditiva para análise de sustentabilidade fiscal e risco soberano.')
    
    # Carregue dados do Brasil
    try:
        data_br = load_brazil_data()
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label='Dívida/PIB (Atual)',
                value=f"{data_br['Divida_PIB'].iloc[-1]:.1f}%",
                delta=f"{data_br['Divida_PIB'].iloc[-1] - data_br['Divida_PIB'].iloc[-30]:.1f}%",
                delta_color='inverse'
            )
        
        with col2:
            st.metric(
                label='Risco Brasil (EMBI+)',
                value=f"{data_br['Risco_Brasil'].iloc[-1]:.0f}",
                delta=f"{data_br['Risco_Brasil'].iloc[-1] - data_br['Risco_Brasil'].iloc[-30]:.0f}",
                delta_color='inverse'
            )
        
        with col3:
            st.metric(
                label='Taxa de Juros Real',
                value=f"{data_br['Juro_Real'].iloc[-1]:.2f}%",
                delta=f"{data_br['Juro_Real'].iloc[-1] - data_br['Juro_Real'].iloc[-30]:.2f}%"
            )
        
        with col4:
            st.metric(
                label='Erro de Previsão',
                value=f"{abs(data_br['Erro_Previsao'].iloc[-1]):.2f}",
                delta="Modelo em ajuste"
            )
        
        # Gráficos
        st.markdown('### 📈 Evolução Temporal')
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.line_chart(data_br[['Divida_PIB', 'Risco_Brasil']].apply(lambda x: (x - x.min()) / (x.max() - x.min())))
            st.caption('Série Normalizada: Dívida/PIB vs Risco Brasil')
        
        with col_chart2:
            st.line_chart(data_br[['Juro_Real']])
            st.caption('Taxa de Juros Real')
        
        # SPJ Econometrics
        st.markdown('### 🔬 Regressão SPJ (Structural Policy Jump)')
        spj_formula = "Risco_Brasil ~ Divida_PIB + Juro_Real"
        spj_results = run_spj(data_br, spj_formula)
        
        col_spj1, col_spj2 = st.columns(2)
        with col_spj1:
            st.write('**Coeficientes Estimados:**')
            for coef, value in spj_results.items():
                st.write(f"- {coef}: {value:.4f}")
        
        with col_spj2:
            st.write('**Interpretação:**')
            st.write(
                f"""- A cada 1% de aumento na Dívida/PIB, o Risco Brasil aumenta {spj_results['Divida_PIB']:.4f} pbs\n
- A elasticidade da taxa de juros é de {spj_results['Juro_Real']:.4f}"""
            )
    
    except Exception as e:
        st.error(f'❌ Erro ao carregar dados: {str(e)}')
        st.info('Verifique a conexão com as APIs de dados (FRED, BCB, IPEA).')

# ============================================================================
# PAGE 2: SIMULAÇÕES
# ============================================================================
elif page == '📈 Simulações':
    st.markdown("<h1 class='main-header'>📈 Simulador de Trajetória da Dívida</h1>", unsafe_allow_html=True)
    st.write('Use `simulate_debt_trajectory()` do módulo `macrolab.dynamics` para projetar a dívida.')
    
    st.markdown('---')
    
    # Sidebar para parâmetros
    st.sidebar.subheader('⚙️ Parâmetros da Simulação')
    
    col_sim1, col_sim2 = st.columns(2)
    
    with col_sim1:
        years = st.slider('Horizonte de Projeção (anos)', 1, 30, 10)
        initial_debt = st.number_input('Dívida Inicial (% PIB)', 40.0, 150.0, 80.0, step=1.0)
    
    with col_sim2:
        interest_rate = st.number_input('Taxa de Juros Nominal (%)', 0.5, 20.0, 8.0, step=0.5) / 100
        growth_rate = st.number_input('Taxa de Crescimento (%)', -5.0, 10.0, 2.0, step=0.5) / 100
    
    primary_balance = st.number_input('Resultado Primário (% PIB)', -10.0, 10.0, -3.0, step=0.5)
    
    # Simulação
    trajectory = simulate_debt_trajectory(
        years=years,
        initial_debt=initial_debt,
        interest_rate=interest_rate,
        growth_rate=growth_rate,
        primary_balance=primary_balance
    )
    
    # Preparar dados para visualização
    df_traj = pd.DataFrame({
        'Ano': range(years),
        'Dívida/PIB (%)': trajectory
    })
    
    # Gráfico
    st.line_chart(df_traj.set_index('Ano'))
    
    # Tabela
    st.markdown('### 📋 Resultados Detalhados')
    st.dataframe(
        df_traj.style.format({'Dívida/PIB (%)': '{:.2f}'}),
        use_container_width=True
    )
    
    # Análise
    st.markdown('### 📊 Análise da Trajetória')
    
    col_ana1, col_ana2, col_ana3 = st.columns(3)
    
    with col_ana1:
        final_debt = trajectory[-1]
        st.metric(
            'Dívida Final',
            f'{final_debt:.1f}%',
            f'{final_debt - initial_debt:+.1f}%',
            delta_color='inverse' if final_debt > initial_debt else 'normal'
        )
    
    with col_ana2:
        trend = 'Crescimento' if trajectory[-1] > trajectory[0] else 'Redução'
        st.metric('Tendência', trend)
    
    with col_ana3:
        volatility = np.std([trajectory[i+1] - trajectory[i] for i in range(len(trajectory)-1)])
        st.metric('Volatilidade Anual', f'{volatility:.3f}%')
    
    # Insights
    st.markdown('### 💡 Insights')
    
    if final_debt > initial_debt:
        st.warning(
            f'⚠️ Trajetória **insustentável**: Dívida cresce de {initial_debt:.1f}% para {final_debt:.1f}% do PIB.'
        )
    else:
        st.success(
            f'✅ Trajetória **sustentável**: Dívida reduz de {initial_debt:.1f}% para {final_debt:.1f}% do PIB.'
        )
    
    if primary_balance < 0:
        st.info(f'📌 Com déficit primário de {primary_balance:.1f}%, esforço fiscal é necessário para estabilizar.')
    else:
        st.success(f'📌 Superávit primário de {primary_balance:.1f}% favorece redução da dívida.')

# ============================================================================
# PAGE 3: DADOS HISTÓRICOS
# ============================================================================
elif page == '📊 Dados Históricos':
    st.markdown("<h1 class='main-header'>📊 Dados Históricos</h1>", unsafe_allow_html=True)
    st.write('Visualize os dados carregados do `data_fetch.py`')
    
    st.markdown('---')
    
    try:
        # Carregue dados
        risco_brasil = get_ipea_robust('RISCOBESP')
        
        st.markdown('### 🌍 Risco Brasil (EMBI+ Brasil)')
        st.line_chart(risco_brasil)
        
        st.markdown('### 📋 Tabela de Dados')
        st.dataframe(risco_brasil.head(20))
        
        st.markdown('### 📈 Estatísticas Descritivas')
        st.write(risco_brasil.describe())
    
    except Exception as e:
        st.error(f'❌ Erro ao carregar dados históricos: {str(e)}')
        st.info('Verifique a conexão com a API IPEA.')

# ============================================================================
# PAGE 4: SOBRE
# ============================================================================
elif page == '⚙️ Sobre':
    st.markdown("<h1 class='main-header'>ℹ️ Sobre MacroLab v7</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ### 📚 Descrição do Projeto
    
    **MacroLab v7** é um framework modular de inteligência preditiva desenvolvido para análise de sustentabilidade fiscal e risco soberano.
    
    ### 🏗️ Arquitetura
    
    1. **Camada de Dados**: `macrolab.data_fetch`
       - Integração com FRED, BCB e IPEA
       - Fallback automático para dados históricos
    
    2. **Camada de Lógica**: `macrolab.dynamics` e `macrolab.__init__`
       - Modelos econométricos (VECM, SPJ)
       - Simulação de trajetória de dívida
       - Random Forest para predição
    
    3. **Camada de API**: `backend/app.py`
       - Endpoints Flask para integração
       - Endpoints para predições em tempo real
    
    4. **Camada de Apresentação**: `content/frontend/app.py`
       - Dashboard Streamlit
       - Visualizações interativas
       - Simulador de cenários
    
    ### 🔧 Tecnologias
    
    - **Machine Learning**: Scikit-learn (Random Forest)
    - **Econometria**: Statsmodels (VECM, OLS)
    - **Web Framework**: Flask (Backend), Streamlit (Frontend)
    - **Dados**: Python-BCB, IPEA Data, FRED API
    - **Containerização**: Docker
    - **Deploy**: Render (Backend + Frontend)
    
    ### 👨‍🎓 Autor
    
    **Éuriks Souza Davalo**
    
    Base técnica da tese de mestrado em Economia Aplicada.
    
    ### 📄 Licença
    
    MIT License
    
    ### 🔗 Links
    
    - [GitHub Repository](https://github.com/Euriks27/macrolab-site)
    - [Documentation](#)
    - [API Docs](#)
    """)

# Footer
st.markdown('---')
st.markdown(
    '<div style="text-align: center; color: gray; font-size: 0.9rem;">'
    'MacroLab v7 | Desenvolvido com ❤️ por Éuriks Souza Davalo'
    '</div>',
    unsafe_allow_html=True
)
