"""
Paquete de OCR para (π)NAD
Integra OCR básico y OCR ultra avanzado con Google Document AI
"""

from .ocr_engine import OCREngine

from .ocr_ultra_advanced import (
    DocumentQuality,
    DocumentType,
    DocumentQualityScore,
    ExtractedLineItem,
    SignatureZone,
    OCRUltraAdvanced,
    OCRUltraAdvancedManager,
    ocr_ultra_advanced_manager
)

__all__ = [
    'OCREngine',
    'DocumentQuality',
    'DocumentType',
    'DocumentQualityScore',
    'ExtractedLineItem',
    'SignatureZone',
    'OCRUltraAdvanced',
    'OCRUltraAdvancedManager',
    'ocr_ultra_advanced_manager'
]
