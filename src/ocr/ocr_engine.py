"""
Módulo OCREngine - Motor de OCR usando EasyOCR para (π)NAD
Adaptado de CONTADOR V6.1 para sistema de contabilidad automatizada
"""

import easyocr
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import cv2
from PIL import Image
import re


class OCREngine:
    """Motor de OCR usando EasyOCR - Adaptado para (π)NAD"""
    
    def __init__(self, languages: List[str] = None, use_gpu: bool = False, 
                 confidence_threshold: float = 0.7):
        """
        Inicializar motor OCR para (π)NAD
        
        Args:
            languages: Lista de idiomas (default: ['es'])
            use_gpu: Usar GPU si está disponible
            confidence_threshold: Umbral de confianza
        """
        self.languages = languages or ['es']
        self.use_gpu = use_gpu
        self.confidence_threshold = confidence_threshold
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Inicializar lector EasyOCR"""
        try:
            self.reader = easyocr.Reader(self.languages, gpu=self.use_gpu)
            print("OCR Engine inicializado exitosamente")
        except Exception as e:
            print(f"Error inicializando EasyOCR: {e}")
            self.reader = None
    
    def extract_text(self, image_path: str, detail: int = 1, 
                    paragraph: bool = True) -> List:
        """
        Extraer texto de imagen
        
        Args:
            image_path: Ruta de la imagen
            detail: Nivel de detalle (0: solo texto, 1: texto + coordenadas)
            paragraph: Agrupar texto en párrafos
            
        Returns:
            Lista de resultados de OCR
        """
        if not self.reader:
            print("OCR reader no inicializado")
            return []
        
        try:
            result = self.reader.readtext(image_path, detail=detail, paragraph=paragraph)
            return result
        except Exception as e:
            print(f"Error extrayendo texto: {e}")
            return []
    
    def extract_text_with_confidence(self, image_path: str) -> List[Dict]:
        """
        Extraer texto con información de confianza
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Lista de diccionarios con texto y confianza
        """
        results = self.extract_text(image_path, detail=1, paragraph=False)
        
        filtered_results = []
        for result in results:
            bbox, text, confidence = result
            if confidence >= self.confidence_threshold:
                filtered_results.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        return filtered_results
    
    def extract_text_only(self, image_path: str) -> str:
        """
        Extraer solo texto (sin coordenadas)
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Texto extraído como string
        """
        results = self.extract_text(image_path, detail=0, paragraph=True)
        return '\n'.join(results)
    
    def extract_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extraer texto de PDF (cada página como string)
        
        Args:
            pdf_path: Ruta del PDF
            
        Returns:
            Lista de strings (una por página)
        """
        try:
            import pypdfium2 as pdfium
            
            pdf = pdfium.PdfDocument(pdf_path)
            page_texts = []
            
            for i in range(len(pdf)):
                page = pdf[i]
                image = page.render(scale=2).to_pil()
                
                # Guardar imagen temporal
                temp_path = f"temp_page_{i}.png"
                image.save(temp_path)
                
                # Extraer texto
                text = self.extract_text_only(temp_path)
                page_texts.append(text)
                
                # Eliminar imagen temporal
                import os
                os.remove(temp_path)
            
            pdf.close()
            return page_texts
            
        except ImportError:
            print("pypdfium2 no instalado. Instala con: pip install pypdfium2")
            return []
        except Exception as e:
            print(f"Error extrayendo de PDF: {e}")
            return []
    
    def extract_invoice_data(self, image_path: str) -> Dict:
        """
        Extraer datos específicos de factura para (π)NAD
        
        Args:
            image_path: Ruta de la imagen de factura
            
        Returns:
            Diccionario con datos extraídos de la factura
        """
        text = self.extract_text_only(image_path)
        
        # Patrones para extraer datos de factura venezolana
        invoice_data = {
            'invoice_number': self._extract_invoice_number(text),
            'rif': self._extract_rif(text),
            'date': self._extract_date(text),
            'total': self._extract_total(text),
            'tax_amount': self._extract_tax_amount(text),
            'raw_text': text
        }
        
        return invoice_data
    
    def extract_report_z_data(self, image_path: str) -> Dict:
        """
        Extraer datos específicos de Reporte Z para (π)NAD
        
        Args:
            image_path: Ruta de la imagen de Reporte Z
            
        Returns:
            Diccionario con datos extraídos del Reporte Z
        """
        text = self.extract_text_only(image_path)
        
        # Patrones para extraer datos de Reporte Z
        report_z_data = {
            'report_date': self._extract_date(text),
            'report_number': self._extract_report_number(text),
            'total_sales': self._extract_total_sales(text),
            'total_tax': self._extract_total_tax(text),
            'cash_sales': self._extract_cash_sales(text),
            'credit_sales': self._extract_credit_sales(text),
            'returns': self._extract_returns(text),
            'raw_text': text
        }
        
        return report_z_data
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extraer número de factura"""
        patterns = [
            r'Factura\s*N[°°]\s*([A-Z0-9-]+)',
            r'N[°°]\s*([A-Z0-9-]+)',
            r'Invoice\s*[#]\s*([A-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_rif(self, text: str) -> Optional[str]:
        """Extraer RIF venezolano"""
        patterns = [
            r'[JVEG]-\d{8}-\d',
            r'RIF[:\s]*([JVEG]-\d{8}-\d)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0) if pattern == patterns[0] else match.group(1)
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extraer fecha"""
        patterns = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{4}/\d{2}/\d{2}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _extract_total(self, text: str) -> Optional[float]:
        """Extraer monto total"""
        patterns = [
            r'Total[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Monto\s*Total[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Suma[:\s]*\$?[\s,]*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        return None
    
    def _extract_tax_amount(self, text: str) -> Optional[float]:
        """Extraer monto de impuesto"""
        patterns = [
            r'IVA[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Impuesto[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Tax[:\s]*\$?[\s,]*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        return None
    
    def _extract_report_number(self, text: str) -> Optional[str]:
        """Extraer número de reporte Z"""
        patterns = [
            r'Reporte\s*Z[:\s]*([A-Z0-9-]+)',
            r'Z[-]\s*([A-Z0-9-]+)',
            r'Report\s*Z[:\s]*([A-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_total_sales(self, text: str) -> Optional[float]:
        """Extraer ventas totales del Reporte Z"""
        patterns = [
            r'Ventas\s*Totales?[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Total\s*Ventas?[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Gross\s*Sales[:\s]*\$?[\s,]*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        return None
    
    def _extract_total_tax(self, text: str) -> Optional[float]:
        """Extraer impuesto total del Reporte Z"""
        patterns = [
            r'IVA\s*Total[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Total\s*IVA[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Total\s*Tax[:\s]*\$?[\s,]*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        return None
    
    def _extract_cash_sales(self, text: str) -> Optional[float]:
        """Extraer ventas al contado"""
        patterns = [
            r'Ventas\s*Contado[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Cash\s*Sales[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Efectivo[:\s]*\$?[\s,]*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        return None
    
    def _extract_credit_sales(self, text: str) -> Optional[float]:
        """Extraer ventas al crédito"""
        patterns = [
            r'Ventas\s*Crédito[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Credit\s*Sales[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Crédito[:\s]*\$?[\s,]*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        return None
    
    def _extract_returns(self, text: str) -> Optional[float]:
        """Extraer devoluciones"""
        patterns = [
            r'Devoluciones?[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Returns?[:\s]*\$?[\s,]*(\d+\.?\d*)',
            r'Rembolsos?[:\s]*\$?[\s,]*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    pass
        return None
