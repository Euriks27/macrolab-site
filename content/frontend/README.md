# MacroLab v7 - Frontend (Dashboard Streamlit)

Interface de apresentação do framework MacroLab v7, desenvolvida com **Streamlit**.

## 📦 Estrutura

```
content/frontend/
├── app.py                    # Dashboard principal
├── test_dashboard.py         # Script de validação
├── utils.py                  # Funções auxiliares
├── .streamlit/
│   └── config.toml          # Configuração Streamlit
├── requirements.txt          # Dependências
└── README.md                 # Este arquivo
```

## 🚀 Quick Start

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Testar integração

```bash
python test_dashboard.py
```

Este script valida:
- ✅ Importação de módulos `macrolab`
- ✅ Função `simulate_debt_trajectory()`
- ✅ Carregamento de dados do Brasil
- ✅ Regressão SPJ
- ✅ Conectividade com API backend

### 3. Executar o dashboard

```bash
streamlit run app.py
```

O dashboard abrirá em `http://localhost:8501`

## 📊 Funcionalidades

### 🏠 Dashboard Principal
- Métricas em tempo real (Dívida/PIB, Risco Brasil, Taxa de Juros)
- Gráficos de evolução temporal
- Regressão SPJ com coeficientes estimados

### 📈 Simulador de Trajetória
- Projete a dívida para diferentes cenários
- Parâmetros interativos:
  - Horizonte de projeção
  - Dívida inicial
  - Taxa de juros
  - Taxa de crescimento
  - Resultado primário
- Análise de sustentabilidade

### 📊 Dados Históricos
- Visualização do Risco Brasil (EMBI+)
- Tabelas com dados brutos
- Estatísticas descritivas

### ⚙️ Sobre
- Documentação da arquitetura
- Stack tecnológico
- Links úteis

## 🔗 Integração com Macrolab Core

O dashboard importa funções do core:

```python
from macrolab.dynamics import simulate_debt_trajectory
from macrolab.data_fetch import get_ipea_robust
from macrolab import load_brazil_data, run_spj
```

### `simulate_debt_trajectory()`

Calcula a trajetória da dívida usando a equação dinâmica:

```
D_t = D_{t-1} * (1+r)/(1+g) - PB
```

Onde:
- `D_t`: Dívida no período t
- `r`: Taxa de juros nominal
- `g`: Taxa de crescimento do PIB
- `PB`: Resultado primário (% PIB)

### `load_brazil_data()`

Carrega dados macroeconômicos do Brasil (simulados ou reais):
- Divida/PIB
- Risco Brasil
- Taxa de Juros Real
- Erro de Previsão

### `run_spj()`

Executa regressão econométrica para estimar relação entre variáveis:
- Intercept
- Coeficientes para cada variável independente

## 🛠️ Utilitários

Arquivo `utils.py` contém funções auxiliares:

- `format_number()`: Formatação de números
- `calculate_sustainability_score()`: Score de sustentabilidade (0-100)
- `get_sustainability_label()`: Label e cor baseado no score
- `simulate_scenarios()`: Múltiplos cenários (otimista, base, pessimista)
- `create_comparison_dataframe()`: DataFrame para comparação
- `get_data_quality_report()`: Relatório de qualidade dos dados
- `export_results()`: Exportar resultados para CSV

## 🌐 Deploy na Render

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "content/frontend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

### Environment Variables

```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_CLIENT_TOOLBARBUTTONPOSITION=bottom
```

## 📝 Notas para a Tese

### Capítulo de Arquitetura

O `/content/frontend` representa a **Camada de Apresentação (UI)** da arquitetura:

```
┌─────────────────────────────────────────┐
│   Camada de Apresentação (Frontend)     │
│   - Dashboard Streamlit                 │
│   - Visualizações Interativas            │
│   - Interface com Usuário                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Camada de Lógica (Macrolab Core)      │
│   - dynamics.py (simulate_debt_trajectory)   │
│   - data_fetch.py (get_ipea_robust)     │
│   - Econometria (VECM, SPJ)              │
│   - Machine Learning (Random Forest)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Camada de Inteligência (Backend API)  │
│   - Flask API (backend/app.py)          │
│   - Endpoints para Predições             │
│   - Serviços de Análise                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Camada de Dados (Data Sources)        │
│   - FRED (Federal Reserve Economic Data)│
│   - BCB (Banco Central do Brasil)       │
│   - IPEA (Instituto de Pesquisa)        │
└─────────────────────────────────────────┘
```

## 🧪 Testes

```bash
# Teste de integração
python test_dashboard.py

# Teste unitário (pytest)
pytest tests/
```

## 📚 Referências

- [Streamlit Docs](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org/docs)
- [Scikit-learn](https://scikit-learn.org)
- [Statsmodels](https://www.statsmodels.org)

## 👨‍💻 Autor

**Éuriks Souza Davalo**

Mestrado em Economia Aplicada | Tese sobre Sustentabilidade Fiscal e Risco Soberano

## 📄 Licença

MIT License
