#!/usr/bin/env python3
"""
🧪 MacroLab v7 - Suite de Testes de Deploy
Valida performance, tratamento de erros e funcionalidade da API
"""

import requests
import json
import time
from typing import Tuple, Dict, List

# Configuração
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    def __init__(self, name: str, passed: bool, latency: float, message: str = ""):
        self.name = name
        self.passed = passed
        self.latency = latency
        self.message = message

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}  {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_test(result: TestResult):
    """Imprime resultado de um teste"""
    status = f"{Colors.GREEN}✅{Colors.RESET}" if result.passed else f"{Colors.RED}❌{Colors.RESET}"
    print(f"{status} {result.name} ({result.latency:.1f}ms)")
    if result.message:
        print(f"   └─ {result.message}")

def test_health_check() -> TestResult:
    """Test 1: Health check endpoint"""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            model_status = data.get('model_status', 'desconhecido')
            message = f"Servidor respondendo | Modelo: {model_status}"
            return TestResult("Health Check", True, latency, message)
        else:
            return TestResult("Health Check", False, latency, f"Status {response.status_code}")
    except Exception as e:
        return TestResult("Health Check", False, 0, str(e))

def test_status_endpoint() -> TestResult:
    """Test 2: Status endpoint"""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/status", timeout=TIMEOUT)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            model_loaded = data.get('model_loaded', False)
            message = f"Status válido | Modelo carregado: {model_loaded}"
            return TestResult("Status Endpoint", True, latency, message)
        else:
            return TestResult("Status Endpoint", False, latency, f"Status {response.status_code}")
    except Exception as e:
        return TestResult("Status Endpoint", False, 0, str(e))

def test_predict_valid() -> TestResult:
    """Test 3: Predict com parâmetros válidos"""
    try:
        payload = {
            "risco": 350,
            "juros": 7.5
        }
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            pred = data.get('prediction_divida_pib', 'N/A')
            message = f"Predição: Dívida/PIB = {pred}% | Latência: {latency:.1f}ms"
            return TestResult("Predict (Válido)", True, latency, message)
        else:
            return TestResult("Predict (Válido)", False, latency, f"Status {response.status_code}")
    except Exception as e:
        return TestResult("Predict (Válido)", False, 0, str(e))

def test_predict_invalid_range() -> TestResult:
    """Test 4: Validação de risco muito alto"""
    try:
        payload = {
            "risco": 1000,  # Fora do range 100-800
            "juros": 7.5
        }
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        latency = (time.time() - start) * 1000
        
        if response.status_code == 422:
            message = f"Validação funcionando | Erro capturado corretamente"
            return TestResult("Validate (Risco Alto)", True, latency, message)
        else:
            return TestResult("Validate (Risco Alto)", False, latency, f"Esperado 422, obtido {response.status_code}")
    except Exception as e:
        return TestResult("Validate (Risco Alto)", False, 0, str(e))

def test_predict_invalid_json() -> TestResult:
    """Test 5: Rejeição de JSON inválido"""
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/predict",
            data="invalid json",
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        latency = (time.time() - start) * 1000
        
        if response.status_code == 400:
            message = f"JSON inválido rejeitado corretamente"
            return TestResult("Reject (JSON Inválido)", True, latency, message)
        else:
            return TestResult("Reject (JSON Inválido)", False, latency, f"Esperado 400, obtido {response.status_code}")
    except Exception as e:
        return TestResult("Reject (JSON Inválido)", False, 0, str(e))

def test_not_found() -> TestResult:
    """Test 6: Tratamento de 404"""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/endpoint-inexistente", timeout=TIMEOUT)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 404:
            message = f"Endpoint 404 tratado corretamente"
            return TestResult("404 Handler", True, latency, message)
        else:
            return TestResult("404 Handler", False, latency, f"Esperado 404, obtido {response.status_code}")
    except Exception as e:
        return TestResult("404 Handler", False, 0, str(e))

def test_performance() -> TestResult:
    """Test 7: Performance com múltiplas requisições"""
    try:
        payload = {
            "risco": 300,
            "juros": 6.0
        }
        latencies = []
        
        for _ in range(10):
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/predict",
                json=payload,
                timeout=TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            latency = (time.time() - start) * 1000
            if response.status_code == 200:
                latencies.append(latency)
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            message = f"10 requisições | Latência média: {avg_latency:.1f}ms"
            passed = avg_latency < 500  # Performance threshold
            return TestResult("Performance (10x)", passed, avg_latency, message)
        else:
            return TestResult("Performance (10x)", False, 0, "Nenhuma requisição bem-sucedida")
    except Exception as e:
        return TestResult("Performance (10x)", False, 0, str(e))

def main():
    """Executa todos os testes"""
    print_header("🧪 MacroLab v7 - Suite de Testes de Deploy")
    
    # Verifica se o servidor está rodando
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Erro: Servidor não está respondendo em {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Inicie o servidor com: python -m flask --app backend.app run{Colors.RESET}")
        return
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao conectar: {e}{Colors.RESET}")
        return
    
    # Executa testes
    tests = [
        test_health_check(),
        test_status_endpoint(),
        test_predict_valid(),
        test_predict_invalid_range(),
        test_predict_invalid_json(),
        test_not_found(),
        test_performance()
    ]
    
    # Imprime resultados
    print_header("📋 Resultados dos Testes")
    for test in tests:
        print_test(test)
    
    # Resumo
    passed = sum(1 for t in tests if t.passed)
    total = len(tests)
    
    print_header("📊 Resumo dos Testes")
    print(f"{Colors.GREEN}✅ Passou:    {passed}/{total}{Colors.RESET}")
    print(f"{Colors.RED}❌ Falhou:    {total - passed}/{total}{Colors.RESET}")
    print(f"📈 Taxa:      {(passed/total)*100:.1f}%")
    
    # Mensagem final
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}🎉  Todos os testes críticos passaram!{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}🎉  O backend está pronto para deploy na Render! 🚀{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Alguns testes falharam. Verifique os erros acima.{Colors.RESET}\n")

if __name__ == "__main__":
    main()
