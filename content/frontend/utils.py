"""
Utilitários para o Dashboard MacroLab v7
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from macrolab.dynamics import simulate_debt_trajectory
from macrolab.data_fetch import get_ipea_robust


def format_number(value: float, decimals: int = 2, prefix: str = '', suffix: str = '') -> str:
    """
    Formata um número para exibição no dashboard
    
    Args:
        value: Número a formatar
        decimals: Casas decimais
        prefix: Prefixo (ex: 'R$')
        suffix: Sufixo (ex: '%')
    
    Returns:
        String formatada
    """
    formatted = f"{value:,.{decimals}f}"
    return f"{prefix}{formatted}{suffix}"


def calculate_sustainability_score(trajectory: List[float]) -> float:
    """
    Calcula um score de sustentabilidade da trajetória da dívida (0-100)
    
    Args:
        trajectory: Lista de valores de dívida/PIB
    
    Returns:
        Score de 0 a 100 (quanto maior, mais sustentável)
    """
    if len(trajectory) < 2:
        return 50.0
    
    initial = trajectory[0]
    final = trajectory[-1]
    trend = -((final - initial) / initial) * 100  # Redução é positiva
    volatility = np.std([trajectory[i+1] - trajectory[i] for i in range(len(trajectory)-1)])
    
    score = 50 + (trend / 2) - (volatility * 5)
    return max(0, min(100, score))  # Limita entre 0 e 100


def get_sustainability_label(score: float) -> Tuple[str, str]:
    """
    Retorna label e cor baseado no score de sustentabilidade
    
    Args:
        score: Score de 0 a 100
    
    Returns:
        Tupla (label, cor)
    """
    if score >= 80:
        return 'Sustentável', 'green'
    elif score >= 60:
        return 'Moderadamente Sustentável', 'yellow'
    elif score >= 40:
        return 'Crítico', 'orange'
    else:
        return 'Insustentável', 'red'


def simulate_scenarios(base_params: Dict) -> Dict:
    """
    Executa múltiplas simulações com variações de parâmetros
    
    Args:
        base_params: Dicionário com parâmetros base:
            - years: int
            - initial_debt: float
            - interest_rate: float
            - growth_rate: float
            - primary_balance: float
    
    Returns:
        Dicionário com cenários: otimista, base, pessimista
    """
    scenarios = {}
    
    # Cenário Pessimista
    scenarios['pessimista'] = simulate_debt_trajectory(
        years=base_params['years'],
        initial_debt=base_params['initial_debt'],
        interest_rate=base_params['interest_rate'] * 1.2,  # +20% juros
        growth_rate=base_params['growth_rate'] * 0.5,      # -50% crescimento
        primary_balance=base_params['primary_balance'] - 2  # -2% déficit
    )
    
    # Cenário Base
    scenarios['base'] = simulate_debt_trajectory(**base_params)
    
    # Cenário Otimista
    scenarios['otimista'] = simulate_debt_trajectory(
        years=base_params['years'],
        initial_debt=base_params['initial_debt'],
        interest_rate=base_params['interest_rate'] * 0.8,   # -20% juros
        growth_rate=base_params['growth_rate'] * 1.5,       # +50% crescimento
        primary_balance=base_params['primary_balance'] + 2  # +2% superávit
    )
    
    return scenarios


def create_comparison_dataframe(scenarios: Dict) -> pd.DataFrame:
    """
    Cria DataFrame para comparação de cenários
    
    Args:
        scenarios: Dicionário com cenários de simulação
    
    Returns:
        DataFrame formatado para visualização
    """
    df = pd.DataFrame({
        'Ano': range(len(scenarios['base'])),
        'Otimista': scenarios['otimista'],
        'Base': scenarios['base'],
        'Pessimista': scenarios['pessimista']
    })
    return df.set_index('Ano')


def get_data_quality_report(data: pd.DataFrame) -> Dict:
    """
    Gera relatório de qualidade dos dados
    
    Args:
        data: DataFrame com dados
    
    Returns:
        Dicionário com métricas de qualidade
    """
    return {
        'total_records': len(data),
        'missing_values': data.isnull().sum().to_dict(),
        'date_range': f"{data.index[0]} a {data.index[-1]}",
        'columns': list(data.columns),
        'data_types': data.dtypes.to_dict()
    }


def export_results(trajectory: List[float], filename: str = 'resultados.csv'):
    """
    Exporta resultados da simulação para CSV
    
    Args:
        trajectory: Lista de valores da trajetória
        filename: Nome do arquivo de saída
    """
    df = pd.DataFrame({
        'Ano': range(len(trajectory)),
        'Divida_PIB': trajectory
    })
    df.to_csv(filename, index=False)
    return filename
