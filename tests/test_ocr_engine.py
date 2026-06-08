"""
Tests para el motor OCR
"""

import pytest
import os
from src.ocr.ocr_engine import OCREngine


class TestOCREngine:
    """Tests para OCREngine"""
    
    @pytest.fixture
    def ocr_engine(self):
        """Fixture para OCREngine"""
        return OCREngine()
    
    def test_initialization(self, ocr_engine):
        """Test de inicialización"""
        assert ocr_engine is not None
        assert ocr_engine.reader is not None
    
    def test_extract_text_no_file(self, ocr_engine):
        """Test de extracción de texto sin archivo"""
        result = ocr_engine.extract_text('nonexistent.jpg')
        assert result['success'] is False
        assert 'error' in result
    
    def test_extract_invoice_data_no_file(self, ocr_engine):
        """Test de extracción de datos de factura sin archivo"""
        result = ocr_engine.extract_invoice_data('nonexistent.jpg')
        assert result['success'] is False
        assert 'error' in result
    
    def test_extract_report_z_data_no_file(self, ocr_engine):
        """Test de extracción de datos de Reporte Z sin archivo"""
        result = ocr_engine.extract_report_z_data('nonexistent.jpg')
        assert result['success'] is False
        assert 'error' in result
