"""
Integration Tests para (π)NAD V6.0
Tests de integración para API REST
"""

import pytest
import requests
import json
from typing import Dict, Any
from datetime import datetime


class TestAPIIntegration:
    """Tests de integración para API REST"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para tests"""
        self.base_url = "http://localhost:5000/api/v1"
        self.auth_token = None
        
        # Crear usuario de test
        self.test_user = {
            "email": "test@pinad.com",
            "password": "test123",
            "name": "Test User"
        }
    
    def test_health_check(self):
        """Test de health check"""
        response = requests.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_user_registration(self):
        """Test de registro de usuario"""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=self.test_user
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["email"] == self.test_user["email"]
    
    def test_user_login(self):
        """Test de login de usuario"""
        # Primero registrar usuario
        requests.post(
            f"{self.base_url}/auth/register",
            json=self.test_user
        )
        
        # Luego hacer login
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data["data"]
        
        # Guardar token para tests siguientes
        self.auth_token = data["data"]["token"]
    
    def test_get_documents_without_auth(self):
        """Test de obtener documentos sin autenticación"""
        response = requests.get(f"{self.base_url}/documents")
        
        assert response.status_code == 401
    
    def test_get_documents_with_auth(self):
        """Test de obtener documentos con autenticación"""
        # Login primero
        self.test_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        response = requests.get(
            f"{self.base_url}/documents",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "documents" in data["data"]
    
    def test_upload_document(self):
        """Test de carga de documento"""
        # Login primero
        self.test_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        # Crear archivo de test
        test_file = {
            "file": ("test.pdf", b"test content", "application/pdf"),
            "name": "Test Document",
            "type": "invoice"
        }
        
        response = requests.post(
            f"{self.base_url}/documents",
            headers=headers,
            files=test_file
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_ocr_processing(self):
        """Test de procesamiento OCR"""
        # Login primero
        self.test_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        # Cargar documento primero
        test_file = {
            "file": ("test.pdf", b"test content", "application/pdf"),
            "name": "Test OCR Document",
            "type": "invoice"
        }
        
        upload_response = requests.post(
            f"{self.base_url}/documents",
            headers=headers,
            files=test_file
        )
        
        document_id = upload_response.json()["data"]["id"]
        
        # Procesar con OCR
        ocr_response = requests.post(
            f"{self.base_url}/ocr/process",
            headers=headers,
            json={
                "documentId": document_id,
                "template": "banesco"
            }
        )
        
        assert ocr_response.status_code == 200
        data = ocr_response.json()
        assert data["success"] is True
        assert "ocrData" in data["data"]
    
    def test_financial_statements(self):
        """Test de estados financieros"""
        # Login primero
        self.test_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        response = requests.get(
            f"{self.base_url}/accounting/financial-statements",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "balanceSheet" in data["data"]
        assert "incomeStatement" in data["data"]
    
    def test_tax_calculation(self):
        """Test de cálculo de impuestos"""
        # Login primero
        self.test_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        response = requests.post(
            f"{self.base_url}/tax/calculate",
            headers=headers,
            json={
                "taxType": "iva",
                "period": "2024-01"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "taxAmount" in data["data"]
    
    def test_delete_document(self):
        """Test de eliminación de documento"""
        # Login primero
        self.test_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        # Cargar documento primero
        test_file = {
            "file": ("test.pdf", b"test content", "application/pdf"),
            "name": "Test Delete Document",
            "type": "invoice"
        }
        
        upload_response = requests.post(
            f"{self.base_url}/documents",
            headers=headers,
            files=test_file
        )
        
        document_id = upload_response.json()["data"]["id"]
        
        # Eliminar documento
        delete_response = requests.delete(
            f"{self.base_url}/documents/{document_id}",
            headers=headers
        )
        
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
