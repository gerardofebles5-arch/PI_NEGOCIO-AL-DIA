"""
E2E Tests para OCR de (π)NAD V6.0
Tests End-to-End para flujo de procesamiento OCR
"""

import pytest
import requests
from PIL import Image
import io
from typing import Dict, Any


class TestOCRFlowE2E:
    """Tests E2E para flujo de procesamiento OCR"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para tests E2E de OCR"""
        self.base_url = "http://localhost:5000/api/v1"
        self.auth_token = None
        
        # Datos de test
        self.test_user = {
            "email": "ocr_test@pinad.com",
            "password": "test123",
            "name": "OCR Test User"
        }
        
        # Crear imagen de test
        self.test_image = self._create_test_image()
    
    def _create_test_image(self) -> bytes:
        """Crear imagen de test"""
        img = Image.new('RGB', (800, 600), color='white')
        
        # Agregar texto simple
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "FACTURA #12345", fill='black')
        draw.text((10, 50), "TOTAL: $100.00", fill='black')
        
        # Convertir a bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PDF')
        return img_byte_arr.getvalue()
    
    def test_complete_ocr_flow_with_banesco_template(self):
        """Test E2E de flujo OCR con plantilla Banesco"""
        # Login
        self._login_user()
        
        # Cargar documento
        document_id = self._upload_document()
        
        # Procesar con OCR usando plantilla Banesco
        ocr_result = self._process_ocr(document_id, "banesco")
        
        # Verificar resultado
        assert ocr_result["success"] is True
        assert "ocrData" in ocr_result["data"]
        assert ocr_result["data"]["ocrData"]["template"] == "banesco"
        assert ocr_result["data"]["confidence"] > 0.8
    
    def test_complete_ocr_flow_with_mercantil_template(self):
        """Test E2E de flujo OCR con plantilla Mercantil"""
        # Login
        self._login_user()
        
        # Cargar documento
        document_id = self._upload_document()
        
        # Procesar con OCR usando plantilla Mercantil
        ocr_result = self._process_ocr(document_id, "mercantil")
        
        # Verificar resultado
        assert ocr_result["success"] is True
        assert "ocrData" in ocr_result["data"]
        assert ocr_result["data"]["ocrData"]["template"] == "mercantil"
    
    def test_ocr_with_invalid_template(self):
        """Test OCR con plantilla inválida"""
        # Login
        self._login_user()
        
        # Cargar documento
        document_id = self._upload_document()
        
        # Intentar procesar con plantilla inválida
        ocr_result = self._process_ocr(document_id, "invalid_template")
        
        # Verificar error
        assert ocr_result["success"] is False
        assert "error" in ocr_result
    
    def test_ocr_with_corrupted_document(self):
        """Test OCR con documento corrupto"""
        # Login
        self._login_user()
        
        # Cargar documento corrupto
        corrupted_data = b"corrupted pdf data"
        document_id = self._upload_document(corrupted_data)
        
        # Intentar procesar con OCR
        ocr_result = self._process_ocr(document_id, "banesco")
        
        # Verificar error
        assert ocr_result["success"] is False
    
    def test_ocr_batch_processing(self):
        """Test de procesamiento OCR en batch"""
        # Login
        self._login_user()
        
        # Cargar múltiples documentos
        document_ids = []
        for i in range(5):
            document_id = self._upload_document()
            document_ids.append(document_id)
        
        # Procesar todos con OCR
        results = []
        for doc_id in document_ids:
            result = self._process_ocr(doc_id, "banesco")
            results.append(result)
        
        # Verificar que todos se procesaron exitosamente
        assert all(r["success"] for r in results)
    
    def test_ocr_with_auto_correction(self):
        """Test OCR con auto-corrección"""
        # Login
        self._login_user()
        
        # Cargar documento
        document_id = self._upload_document()
        
        # Procesar con OCR con auto-corrección
        ocr_result = self._process_ocr(
            document_id,
            "banesco",
            options={"autoCorrect": True}
        )
        
        # Verificar resultado
        assert ocr_result["success"] is True
        assert "ocrData" in ocr_result["data"]
        assert ocr_result["data"]["ocrData"]["autoCorrected"] is True
    
    def _login_user(self):
        """Helper para login de usuario"""
        # Registrar usuario
        requests.post(
            f"{self.base_url}/auth/register",
            json=self.test_user
        )
        
        # Login
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        
        self.auth_token = response.json()["data"]["token"]
    
    def _upload_document(self, data: bytes = None) -> str:
        """Helper para cargar documento"""
        document_data = data or self.test_image
        
        response = requests.post(
            f"{self.base_url}/documents",
            headers={
                "Authorization": f"Bearer {self.auth_token}"
            },
            files={
                "file": ("test.pdf", document_data, "application/pdf"),
                "name": "OCR Test Document",
                "type": "invoice"
            }
        )
        
        return response.json()["data"]["id"]
    
    def _process_ocr(
        self,
        document_id: str,
        template: str,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Helper para procesar documento con OCR"""
        payload = {
            "documentId": document_id,
            "template": template,
            "options": options or {}
        }
        
        response = requests.post(
            f"{self.base_url}/ocr/process",
            headers={
                "Authorization": f"Bearer {self.auth_token}"
            },
            json=payload
        )
        
        return response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
