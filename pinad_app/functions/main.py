"""
Cloud Functions para PINAD Scanning System
Integración del motor OCR propio con Firebase Functions
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import base64

import cv2
import numpy as np
from PIL import Image
import easyocr

from firebase_functions import https_fn
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app, credentials
from supabase import create_client, Client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar opciones globales
set_global_options(max_instances=10)

# Inicializar Firebase Admin
initialize_app()

# Configurar Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://rteuftlsbglpgcawsdqz.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'sb_publishable_eUlKRfeFNvqdURtW_abbIA_N8Qte0l3')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class OCREngine:
    """Motor OCR usando EasyOCR y OpenCV"""
    
    def __init__(self):
        """Inicializar motor OCR"""
        self.reader = easyocr.Reader(['es', 'en'], gpu=False)
        logger.info("Motor OCR inicializado")
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Preprocesar imagen para mejorar OCR"""
        # Convertir bytes a numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar umbral adaptativo
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducir ruido
        denoised = cv2.fastNlMeansDenoising(binary)
        
        return denoised
    
    def extract_text(self, image_data: bytes) -> Dict[str, Any]:
        """Extraer texto de imagen usando EasyOCR"""
        try:
            # Preprocesar imagen
            processed = self.preprocess_image(image_data)
            
            # Extraer texto
            results = self.reader.readtext(processed)
            
            # Procesar resultados
            extracted_text = []
            confidence_scores = []
            
            for (bbox, text, confidence) in results:
                extracted_text.append(text)
                confidence_scores.append(confidence)
            
            # Calcular confianza promedio
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                'text': ' '.join(extracted_text),
                'confidence': avg_confidence,
                'word_count': len(extracted_text),
                'processing_method': 'easyocr',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en extracción OCR: {e}")
            return {
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """Extraer datos específicos de factura del texto"""
        import re
        
        data = {
            'rif': None,
            'invoice_number': None,
            'date': None,
            'amount': None,
            'subtotal': None,
            'iva': None,
            'total': None
        }
        
        # Extraer RIF
        rif_match = re.search(r'[JGVE]-\d{8}-\d', text)
        if rif_match:
            data['rif'] = rif_match.group()
        
        # Extraer número de factura
        invoice_match = re.search(r'(?:factura|n[úu]mero)[:\s]*(\d+)', text, re.IGNORECASE)
        if invoice_match:
            data['invoice_number'] = invoice_match.group(1)
        
        # Extraer fecha
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            data['date'] = date_match.group(1)
        
        # Extraer montos
        amount_matches = re.findall(r'BS[:\s]*([\d.,]+)', text, re.IGNORECASE)
        if amount_matches:
            # El último monto suele ser el total
            amounts = [float(m.replace(',', '')) for m in amount_matches]
            if amounts:
                data['total'] = max(amounts)
                if len(amounts) > 1:
                    data['subtotal'] = amounts[0]
                if len(amounts) > 2:
                    data['iva'] = amounts[1]
        
        return data


# Singleton instance del motor OCR
ocr_engine = OCREngine()


@https_fn.on_request()
def process_document(req: https_fn.Request) -> https_fn.Response:
    """
    Cloud Function para procesar documento con OCR
    """
    # CORS headers
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
        }
        return https_fn.Response('', status=204, headers=headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
    }
    
    try:
        request_json = req.get_json(silent=True)
        
        if not request_json:
            return https_fn.Response(
                json.dumps({'error': 'No JSON data provided'}),
                status=400,
                headers=headers
            )
        
        # Obtener datos
        image_data_base64 = request_json.get('image_data')
        tenant_id = request_json.get('tenant_id')
        user_id = request_json.get('user_id')
        file_name = request_json.get('file_name')
        
        if not image_data_base64:
            return https_fn.Response(
                json.dumps({'error': 'image_data is required'}),
                status=400,
                headers=headers
            )
        
        # Decodificar imagen
        image_data = base64.b64decode(image_data_base64)
        
        # Extraer texto con OCR
        ocr_result = ocr_engine.extract_text(image_data)
        
        if 'error' in ocr_result:
            return https_fn.Response(
                json.dumps(ocr_result),
                status=500,
                headers=headers
            )
        
        # Extraer datos de factura
        invoice_data = ocr_engine.extract_invoice_data(ocr_result['text'])
        
        # Guardar en Supabase
        document_data = {
            'tenant_id': tenant_id,
            'user_id': user_id,
            'file_name': file_name,
            'extracted_data': {
                'text': ocr_result['text'],
                'invoice_data': invoice_data
            },
            'ocr_confidence': ocr_result['confidence'],
            'status': 'processed'
        }
        
        # Insertar en Supabase
        try:
            supabase.table('documents').insert(document_data).execute()
            logger.info(f"Documento guardado en Supabase: {file_name}")
        except Exception as e:
            logger.error(f"Error guardando en Supabase: {e}")
            # Continuar aunque falle el guardado
        
        result = {
            'success': True,
            'text': ocr_result['text'],
            'confidence': ocr_result['confidence'],
            'invoice_data': invoice_data,
            'timestamp': datetime.now().isoformat()
        }
        
        return https_fn.Response(
            json.dumps(result),
            status=200,
            headers=headers
        )
    
    except Exception as e:
        logger.error(f"Error en process_document: {e}")
        return https_fn.Response(
            json.dumps({'error': str(e)}),
            status=500,
            headers=headers
        )


@https_fn.on_request()
def health_check(req: https_fn.Request) -> https_fn.Response:
    """
    Cloud Function para health check
    """
    return https_fn.Response(
        json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'PINAD Scanning System OCR'
        }),
        status=200,
        headers={'Content-Type': 'application/json'}
    )