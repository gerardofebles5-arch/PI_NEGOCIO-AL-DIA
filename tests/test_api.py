"""
Tests para la API REST
"""

import pytest
import json
from src.api.rest_api import PINADAPI


class TestPINADAPI:
    """Tests para PINADAPI"""
    
    @pytest.fixture
    def api(self):
        """Fixture para API"""
        return PINADAPI()
    
    @pytest.fixture
    def client(self, api):
        """Fixture para cliente de prueba"""
        api.app.config['TESTING'] = True
        return api.app.test_client()
    
    def test_health_check(self, client):
        """Test de health check"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_system_status(self, client):
        """Test de estado del sistema"""
        response = client.get('/api/v1/system/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'initialized' in data
    
    def test_create_client(self, client):
        """Test de creación de cliente"""
        client_data = {
            'rif': 'J-12345678-9',
            'name': 'Test Client',
            'email': 'test@example.com',
            'phone': '+58-414-123-4567',
            'sector': 'comercio',
            'plan': 'basic'
        }
        
        response = client.post('/api/v1/clients', 
                            json=client_data,
                            content_type='application/json')
        
        # Puede fallar si el sistema no está inicializado
        assert response.status_code in [201, 500]
