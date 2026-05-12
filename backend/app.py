import os
import joblib
import pandas as pd
import numpy as np
import requests
from flask import Flask, jsonify, request
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 1. Configuração de Sessão Otimizada (Connection Pooling)
def get_api_session():
    """Cria sessão com retry automático e connection pooling"""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

API_SESSION = get_api_session()

# 2. Carregamento Global do Modelo (Caching)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'model_v7.pkl')
MACRO_BRAIN = None

def load_model():
    """Carrega modelo uma única vez ao iniciar a aplicação"""
    global MACRO_BRAIN
    if os.path.exists(MODEL_PATH):
        try:
            MACRO_BRAIN = joblib.load(MODEL_PATH)
            logger.info("✅ MacroLab v7 Brain: Modelo carregado com sucesso.")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar o modelo: {e}")
            MACRO_BRAIN = None
    else:
        logger.warning(f"⚠️ Aviso: Arquivo {MODEL_PATH} não encontrado. Operando em modo limitado.")

# Carrega o modelo no startup da aplicação
load_model()

# 3. Endpoints da API

@app.route('/')
def health_check():
    """Health check para verificar se o servidor está respondendo"""
    model_status = "carregado" if MACRO_BRAIN is not None else "não carregado"
    return jsonify({
        'status': 'online',
        'project': 'MacroLab v7',
        'author': 'Euriks Souza Davalo',
        'version': '7.0.1-stable',
        'model_status': model_status
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint de predição com validação robusta"""
    if MACRO_BRAIN is None:
        logger.error("Tentativa de predição com modelo não carregado")
        return jsonify({'error': 'Modelo não carregado no servidor.'}), 503
    
    try:
        dados = request.get_json()
        
        if dados is None:
            return jsonify({'error': 'Payload JSON inválido'}), 400
        
        # Extração com valores padrão seguros
        risco = float(dados.get('risco', 250))
        juros = float(dados.get('juros', 6.0))
        
        # Validação de ranges
        if not (100 <= risco <= 800) or not (0 <= juros <= 30):
            return jsonify({
                'error': 'Parâmetros fora do intervalo válido',
                'valid_ranges': {'risco': '100-800', 'juros': '0-30'}
            }), 422
        
        # Preparação vetorial para o Random Forest
        df_input = pd.DataFrame(
            [[risco, juros]],
            columns=['risco_brasil', 'juro_real']
        )
        
        # Predição de Dívida/PIB
        pred = MACRO_BRAIN['model'].predict(df_input)[0]
        
        logger.info(f"Predição realizada: risco={risco}, juros={juros}, divida_pib={pred}")
        
        return jsonify({
            'prediction_divida_pib': round(float(pred), 2),
            'parameters': {'risco': risco, 'juros': juros},
            'timestamp': pd.Timestamp.now().isoformat(),
            'model_version': '7.0.1'
        }), 200

    except ValueError as e:
        logger.error(f"Erro de validação: {e}")
        return jsonify({'error': f'Parâmetros inválidos: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Erro inesperado na predição: {e}")
        return jsonify({'error': f'Falha no processamento: {str(e)}'}), 500

@app.route('/status', methods=['GET'])
def status():
    """Retorna status detalhado da aplicação"""
    return jsonify({
        'api_version': '7.0.1-stable',
        'model_loaded': MACRO_BRAIN is not None,
        'environment': os.environ.get('FLASK_ENV', 'production'),
        'timestamp': pd.Timestamp.now().isoformat()
    }), 200

# 4. Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno do servidor: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

# 5. Inicialização para Produção (Render/Gunicorn)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8081))
    logger.info(f"Iniciando MacroLab v7 na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
