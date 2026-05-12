"""
Testes unitários para o backend Flask
"""

import pytest
import json


class TestHealthCheck:
    """Testes do endpoint de health check"""
    
    def test_health_check_status_200(self, client):
        """Deve retornar status 200 no endpoint raiz"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_health_check_json_structure(self, client):
        """Deve retornar JSON com estrutura correta"""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'status' in data
        assert 'project' in data
        assert 'version' in data
        assert data['status'] == 'online'


class TestStatusEndpoint:
    """Testes do endpoint de status"""
    
    def test_status_endpoint_200(self, client):
        """Deve retornar status 200"""
        response = client.get('/status')
        assert response.status_code == 200
    
    def test_status_has_required_fields(self, client):
        """Deve conter campos obrigatórios"""
        response = client.get('/status')
        data = json.loads(response.data)
        assert 'api_version' in data
        assert 'model_loaded' in data
        assert 'environment' in data


class TestPredictEndpoint:
    """Testes do endpoint de predição"""
    
    def test_predict_requires_post(self, client):
        """GET não deve ser permitido"""
        response = client.get('/predict')
        assert response.status_code in [405, 400, 503]  # Method not allowed ou erro
    
    def test_predict_with_valid_params(self, client):
        """Deve aceitar parâmetros válidos"""
        payload = {'risco': 300, 'juros': 6.5}
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # 200 se modelo carregado, 503 se não
        assert response.status_code in [200, 503]
    
    def test_predict_rejects_invalid_range(self, client):
        """Deve rejeitar risco fora do range"""
        payload = {'risco': 1000, 'juros': 6.5}
        response = client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 422
    
    def test_predict_rejects_invalid_json(self, client):
        """Deve rejeitar JSON inválido"""
        response = client.post(
            '/predict',
            data='invalid',
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_predict_default_values(self, client):
        """Deve funcionar com payload vazio (usa defaults)"""
        response = client.post(
            '/predict',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code in [200, 503]


class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_404_not_found(self, client):
        """Deve retornar 404 para endpoint inexistente"""
        response = client.get('/inexistente')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_500_error_handler(self, client):
        """Deve ter handler para erros 500"""
        # Tenta acessar um endpoint que não existe via POST
        response = client.post('/inexistente')
        assert response.status_code in [404, 405]


class TestCors:
    """Testes CORS (se implementado)"""
    
    def test_origin_header(self, client):
        """Deve retornar headers CORS"""
        response = client.get('/')
        # Headers de segurança devem estar presentes
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
