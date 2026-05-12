import requests
import threading
import time
import sys
from backend.app import app

# Função para rodar o Flask em uma thread separada para teste
def run_server():
    try:
        app.run(port=8081, debug=False, use_reloader=False)
    except Exception as e:
        print(f'Erro ao iniciar servidor: {e}')

# Iniciando o servidor
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# Aguarda um momento para o servidor subir
time.sleep(3)

def test_endpoints():
    base_url = 'http://127.0.0.1:8081'

    print("--- Iniciando Testes de API na porta 8081 ---")

    # Testando Home
    try:
        response_home = requests.get(f'{base_url}/')
        print(f"[GET /] Status: {response_home.status_code}")
        print(f"[GET /] Resposta: {response_home.json()}")
    except Exception as e:
        print(f"Erro no teste da Home: {e}")

    # Testando Predict
    try:
        response_pred = requests.get(f'{base_url}/predict')
        print(f"[GET /predict] Status: {response_pred.status_code}")
        print(f"[GET /predict] Resposta: {response_pred.json()}")
    except Exception as e:
        print(f"Erro no teste de Predição: {e}")

if __name__ == '__main__':
    test_endpoints()
    sys.exit(0)