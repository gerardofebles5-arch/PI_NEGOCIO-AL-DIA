"""
Servicio de OCR para extracción de datos de documentos
Conecta con Supabase Edge Function para procesamiento real
"""
import os
import requests
import base64
from typing import Dict, Any

class OCRService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://rteuftlsbglpgcawsdqz.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_KEY", "sb_publishable_eUlKRfeFNvqdURtW_abbIA_N8Qte0l3")
        self.ocr_function_url = f"{self.supabase_url}/functions/v1/ocr"
    
    def process_document(self, file_bytes: bytes, file_name: str) -> Dict[str, Any]:
        """Procesar documento con OCR real"""
        try:
            # Convertir archivo a base64
            file_base64 = base64.b64encode(file_bytes).decode('utf-8')
            
            # Preparar payload para Supabase Edge Function
            payload = {
                "file": file_base64,
                "filename": file_name,
                "type": "invoice"  # Puede ser invoice, receipt, etc.
            }
            
            # Llamar a Supabase Edge Function
            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.ocr_function_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_ocr_result(data)
            else:
                print(f"Error en OCR: {response.status_code} - {response.text}")
                return self._get_fallback_result(file_name)
                
        except Exception as e:
            print(f"Error procesando documento: {e}")
            return self._get_fallback_result(file_name)
    
    def _parse_ocr_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsear resultado de OCR"""
        # Extraer datos del resultado de OCR
        return {
            "success": True,
            "document_type": data.get("document_type", "Factura"),
            "date": data.get("date", ""),
            "amount": data.get("amount", 0.0),
            "tax": data.get("tax", 0.0),
            "total": data.get("total", 0.0),
            "vendor": data.get("vendor", ""),
            "items": data.get("items", []),
            "raw_text": data.get("text", "")
        }
    
    def _get_fallback_result(self, file_name: str) -> Dict[str, Any]:
        """Resultado de fallback cuando OCR falla"""
        return {
            "success": False,
            "document_type": "Desconocido",
            "date": "",
            "amount": 0.0,
            "tax": 0.0,
            "total": 0.0,
            "vendor": "",
            "items": [],
            "raw_text": "",
            "error": "OCR no disponible - usando modo manual"
        }
    
    def extract_invoice_data(self, file_bytes: bytes, file_name: str) -> Dict[str, Any]:
        """Extraer datos específicos de factura"""
        result = self.process_document(file_bytes, file_name)
        
        if result["success"]:
            return {
                "tipo_documento": "Factura",
                "fecha": result["date"],
                "proveedor": result["vendor"],
                "subtotal": result["amount"],
                "iva": result["tax"],
                "total": result["total"],
                "items": result["items"],
                "texto_completo": result["raw_text"]
            }
        else:
            return result
