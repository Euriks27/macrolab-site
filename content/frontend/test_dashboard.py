#!/usr/bin/env python3
"""
Script de Teste do Dashboard Streamlit

Validação de integração entre frontend e backend
Verifica:
- Importação correta de módulos macrolab
- Conectividade com APIs de dados
- Funcionamento do simulador de dívida
- Status da API backend
"""

import sys
import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from macrolab.dynamics import simulate_debt_trajectory
from macrolab.data_fetch import get_ipea_robust
from macrolab import load_brazil_data, run_spj

class DashboardTester:
    """Classe para testar componentes do dashboard"""
    
    def __init__(self):
        self.results = {}
        self.backend_url = 'http://localhost:8081'
    
    def test_imports(self):
        """Testa se todos os módulos podem ser importados corretamente"""
        print('\n[TEST 1] Testando importações...')
        try:
            assert simulate_debt_trajectory is not None
            assert load_brazil_data is not None
            assert run_spj is not None
            assert get_ipea_robust is not None
            print('✅ Todas as importações foram bem-sucedidas!')
            self.results['imports'] = 'PASS'
            return True
        except Exception as e:
            print(f'❌ Erro nas importações: {str(e)}')
            self.results['imports'] = 'FAIL'
            return False
    
    def test_simulate_debt_trajectory(self):
        """Testa a função simulate_debt_trajectory"""
        print('\n[TEST 2] Testando simulate_debt_trajectory...')
        try:
            trajectory = simulate_debt_trajectory(
                years=10,
                initial_debt=80.0,
                interest_rate=0.08,
                growth_rate=0.02,
                primary_balance=-3.0
            )
            
            assert len(trajectory) == 10, "Trajetória deve ter 10 anos"
            assert trajectory[0] == 80.0, "Dívida inicial deve ser 80%"
            assert all(isinstance(x, (int, float)) for x in trajectory), "Todos os valores devem ser números"
            
            print(f'✅ Simulação bem-sucedida:')
            print(f'   Dívida Inicial: {trajectory[0]:.2f}%')
            print(f'   Dívida Final: {trajectory[-1]:.2f}%')
            print(f'   Variação: {trajectory[-1] - trajectory[0]:+.2f}%')
            self.results['simulate_debt_trajectory'] = 'PASS'
            return True
        except Exception as e:
            print(f'❌ Erro na simulação: {str(e)}')
            self.results['simulate_debt_trajectory'] = 'FAIL'
            return False
    
    def test_load_brazil_data(self):
        """Testa carregamento de dados do Brasil"""
        print('\n[TEST 3] Testando load_brazil_data...')
        try:
            df = load_brazil_data()
            
            assert isinstance(df, pd.DataFrame), "Deve retornar DataFrame"
            assert len(df) > 0, "DataFrame não deve estar vazio"
            assert 'Divida_PIB' in df.columns, "Deve ter coluna Divida_PIB"
            assert 'Risco_Brasil' in df.columns, "Deve ter coluna Risco_Brasil"
            
            print(f'✅ Dados carregados com sucesso:')
            print(f'   Período: {df.index[0]} a {df.index[-1]}')
            print(f'   Registros: {len(df)}')
            print(f'   Colunas: {list(df.columns)}')
            self.results['load_brazil_data'] = 'PASS'
            return True
        except Exception as e:
            print(f'❌ Erro ao carregar dados: {str(e)}')
            self.results['load_brazil_data'] = 'FAIL'
            return False
    
    def test_run_spj(self):
        """Testa regressão SPJ"""
        print('\n[TEST 4] Testando run_spj...')
        try:
            df = load_brazil_data()
            results = run_spj(df, "Risco_Brasil ~ Divida_PIB + Juro_Real")
            
            assert isinstance(results, dict), "Deve retornar dicionário"
            assert 'Intercept' in results, "Deve ter Intercept"
            
            print(f'✅ Regressão SPJ bem-sucedida:')
            for coef, value in results.items():
                print(f'   {coef}: {value:.6f}')
            self.results['run_spj'] = 'PASS'
            return True
        except Exception as e:
            print(f'❌ Erro na regressão: {str(e)}')
            self.results['run_spj'] = 'FAIL'
            return False
    
    def test_backend_api(self):
        """Testa conectividade com API backend"""
        print('\n[TEST 5] Testando API Backend...')
        try:
            response = requests.get(f'{self.backend_url}/', timeout=5)
            assert response.status_code == 200, f"Status code: {response.status_code}"
            data = response.json()
            print(f'✅ Backend API respondendo:')
            print(f'   URL: {self.backend_url}')
            print(f'   Status: {data.get("status")}')
            print(f'   Mensagem: {data.get("message")}')
            self.results['backend_api'] = 'PASS'
            return True
        except requests.exceptions.ConnectionError:
            print(f'⚠️  Backend API não está acessível em {self.backend_url}')
            print(f'    Execute: python backend/app.py')
            self.results['backend_api'] = 'WARN'
            return False
        except Exception as e:
            print(f'❌ Erro ao conectar com backend: {str(e)}')
            self.results['backend_api'] = 'FAIL'
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print('\n' + '='*60)
        print('MacroLab v7 - Dashboard Test Suite')
        print('='*60)
        
        self.test_imports()
        self.test_simulate_debt_trajectory()
        self.test_load_brazil_data()
        self.test_run_spj()
        self.test_backend_api()
        
        # Resumo
        print('\n' + '='*60)
        print('RESUMO DOS TESTES')
        print('='*60)
        
        for test_name, result in self.results.items():
            icon = '✅' if result == 'PASS' else '⚠️ ' if result == 'WARN' else '❌'
            print(f'{icon} {test_name}: {result}')
        
        # Estatísticas
        passed = sum(1 for r in self.results.values() if r == 'PASS')
        failed = sum(1 for r in self.results.values() if r == 'FAIL')
        warned = sum(1 for r in self.results.values() if r == 'WARN')
        
        print(f'\nTotal: {passed} passed, {warned} warned, {failed} failed')
        print('='*60 + '\n')
        
        return failed == 0

if __name__ == '__main__':
    tester = DashboardTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
