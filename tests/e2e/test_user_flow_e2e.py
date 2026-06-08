"""
E2E Tests para (π)NAD V6.0
Tests End-to-End para flujo completo de usuario
"""

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
from typing import Dict, Any


class TestUserFlowE2E:
    """Tests E2E para flujo completo de usuario"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para tests E2E"""
        # Configurar Chrome WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Configurar API client
        self.base_url = "http://localhost:5000/api/v1"
        self.app_url = "http://localhost:3000"
        
        # Datos de test
        self.test_user = {
            "email": "e2e_test@pinad.com",
            "password": "test123",
            "name": "E2E Test User"
        }
    
    def test_complete_user_registration_flow(self):
        """Test E2E de flujo completo de registro"""
        # Navegar a la app
        self.driver.get(self.app_url)
        
        # Esperar carga de splash screen
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-button"))
        )
        
        # Hacer clic en registrarse
        register_button = self.driver.find_element(By.ID, "register-link")
        register_button.click()
        
        # Esperar formulario de registro
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "register-form"))
        )
        
        # Llenar formulario
        self.driver.find_element(By.ID, "name-input").send_keys(self.test_user["name"])
        self.driver.find_element(By.ID, "email-input").send_keys(self.test_user["email"])
        self.driver.find_element(By.ID, "password-input").send_keys(self.test_user["password"])
        self.driver.find_element(By.ID, "confirm-password-input").send_keys(self.test_user["password"])
        
        # Enviar formulario
        self.driver.find_element(By.ID, "register-button").click()
        
        # Verificar redirección a dashboard
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        
        # Verificar que el usuario está autenticado
        assert self.driver.current_url == f"{self.app_url}/dashboard"
    
    def test_complete_document_upload_flow(self):
        """Test E2E de flujo completo de carga de documento"""
        # Login primero
        self._login_user()
        
        # Navegar a documentos
        self.driver.get(f"{self.app_url}/documents")
        
        # Hacer clic en cargar documento
        upload_button = self.driver.find_element(By.ID, "upload-document-button")
        upload_button.click()
        
        # Esperar formulario de carga
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "upload-form"))
        )
        
        # Seleccionar archivo
        file_input = self.driver.find_element(By.ID, "file-input")
        file_input.send_keys("/path/to/test/document.pdf")
        
        # Llenar nombre
        self.driver.find_element(By.ID, "document-name").send_keys("Test Document")
        
        # Seleccionar tipo
        type_select = self.driver.find_element(By.ID, "document-type")
        type_select.send_keys("invoice")
        
        # Enviar formulario
        self.driver.find_element(By.ID, "upload-submit-button").click()
        
        # Verificar redirección a lista de documentos
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "documents-list"))
        )
        
        # Verificar que el documento aparece en la lista
        documents = self.driver.find_elements(By.CLASS_NAME, "document-item")
        assert len(documents) > 0
    
    def test_complete_ocr_processing_flow(self):
        """Test E2E de flujo completo de procesamiento OCR"""
        # Login primero
        self._login_user()
        
        # Cargar documento
        self._upload_test_document()
        
        # Navegar a documentos
        self.driver.get(f"{self.app_url}/documents")
        
        # Seleccionar documento
        document_item = self.driver.find_element(By.CLASS_NAME, "document-item")
        document_item.click()
        
        # Esperar detalles del documento
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "document-details"))
        )
        
        # Hacer clic en procesar con OCR
        ocr_button = self.driver.find_element(By.ID, "ocr-process-button")
        ocr_button.click()
        
        # Seleccionar plantilla
        template_select = self.driver.find_element(By.ID, "template-select")
        template_select.send_keys("banesco")
        
        # Confirmar procesamiento
        self.driver.find_element(By.ID, "ocr-confirm-button").click()
        
        # Esperar notificación de éxito
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-notification"))
        )
        
        # Verificar que el documento está procesado
        status_badge = self.driver.find_element(By.CLASS_NAME, "status-badge")
        assert "completado" in status_badge.text.lower()
    
    def test_complete_financial_report_flow(self):
        """Test E2E de flujo completo de reportes financieros"""
        # Login primero
        self._login_user()
        
        # Navegar a contabilidad
        self.driver.get(f"{self.app_url}/accounting")
        
        # Seleccionar balance general
        balance_sheet_tab = self.driver.find_element(By.ID, "balance-sheet-tab")
        balance_sheet_tab.click()
        
        # Esperar carga del reporte
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "balance-sheet-report"))
        )
        
        # Verificar que el reporte se muestra
        report_content = self.driver.find_element(By.CLASS_NAME, "report-content")
        assert report_content.is_displayed()
    
    def test_complete_logout_flow(self):
        """Test E2E de flujo completo de logout"""
        # Login primero
        self._login_user()
        
        # Hacer clic en logout
        logout_button = self.driver.find_element(By.ID, "logout-button")
        logout_button.click()
        
        # Verificar redirección a login
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        
        # Verificar que no está autenticado
        assert self.driver.current_url == f"{self.app_url}/login"
    
    def _login_user(self):
        """Helper para login de usuario"""
        # Registrar usuario primero
        requests.post(
            f"{self.base_url}/auth/register",
            json=self.test_user
        )
        
        # Navegar a login
        self.driver.get(self.app_url)
        
        # Llenar formulario de login
        self.driver.find_element(By.ID, "email-input").send_keys(self.test_user["email"])
        self.driver.find_element(By.ID, "password-input").send_keys(self.test_user["password"])
        
        # Enviar formulario
        self.driver.find_element(By.ID, "login-button").click()
        
        # Esperar dashboard
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
    
    def _upload_test_document(self):
        """Helper para cargar documento de test"""
        # Cargar documento via API
        requests.post(
            f"{self.base_url}/documents",
            headers={
                "Authorization": f"Bearer {self._get_auth_token()}"
            },
            files={
                "file": ("test.pdf", b"test content", "application/pdf"),
                "name": "E2E Test Document",
                "type": "invoice"
            }
        )
    
    def _get_auth_token(self) -> str:
        """Helper para obtener token de autenticación"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        return response.json()["data"]["token"]
    
    def teardown(self):
        """Cleanup después de tests"""
        self.driver.quit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
