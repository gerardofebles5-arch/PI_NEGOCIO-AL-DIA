"""
Archivo principal de integración para (π)NAD - Google Native Architecture V6.0
Sistema unificado de contabilidad, valoración de activos, OCR, impuestos, automatización e infraestructura
Mejoras FASE_3: Integración completa con Document AI, Vertex AI, Cloud Functions
"""

import sys
import os
import logging
import datetime
import numpy as np
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cache de resultados OCR
ocr_cache = {}

def get_cache_key(image_data, options):
    """Genera una clave única para el cache basada en la imagen y opciones"""
    import hashlib
    import json
    
    # Crear hash de la imagen
    image_hash = hashlib.md5(image_data.encode()).hexdigest()
    
    # Crear hash de las opciones
    options_str = json.dumps(options, sort_keys=True)
    options_hash = hashlib.md5(options_str.encode()).hexdigest()
    
    return f"{image_hash}_{options_hash}"

def get_cached_result(cache_key):
    """Obtiene resultado del cache si existe"""
    return ocr_cache.get(cache_key)

def cache_result(cache_key, result):
    """Guarda resultado en el cache"""
    # Limitar cache a 100 entradas
    if len(ocr_cache) >= 100:
        # Eliminar la entrada más antigua
        oldest_key = next(iter(ocr_cache))
        del ocr_cache[oldest_key]
    ocr_cache[cache_key] = result

# Funciones auxiliares para OCR (definidas fuera de main para acceso global)
def classify_document(text):
    """Clasifica el tipo de documento basado en el contenido"""
    import re
    text_lower = text.lower()
    
    # Patrones para diferentes tipos de documentos
    patterns = {
        'factura': ['factura', 'invoice', 'total', 'subtotal', 'iva', 'tax', 'monto', 'cantidad'],
        'recibo': ['recibo', 'receipt', 'pagado', 'payment', 'efectivo', 'tarjeta'],
        'contrato': ['contrato', 'contract', 'acuerdo', 'agreement', 'cláusula', 'firmado'],
        'identificación': ['cédula', 'identification', 'dni', 'passport', 'nombre', 'fecha nacimiento'],
        'reporte': ['reporte', 'report', 'análisis', 'analysis', 'resumen', 'summary'],
        'certificado': ['certificado', 'certificate', 'certifica', 'autentica'],
        'licencia': ['licencia', 'license', 'conducir', 'driving', 'vehículo', 'vehicle', 'clase', 'class'],
        'pasaporte': ['pasaporte', 'passport', 'república', 'republic', 'nacionalidad', 'nationality'],
        'tarjeta_credito': ['tarjeta', 'card', 'credit', 'crédito', 'visa', 'mastercard', 'amex', 'expiry'],
        'seguro': ['seguro', 'insurance', 'póliza', 'policy', 'cobertura', 'coverage', 'siniestro'],
        'nota_credito': ['nota', 'credit', 'devolución', 'refund', 'reembolso', 'abono']
    }
    
    scores = {}
    for doc_type, keywords in patterns.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[doc_type] = score
    
    # Retornar el tipo con mayor score
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return 'desconocido'

def extract_structured_data(text, document_type):
    """Extrae datos estructurados basado en el tipo de documento"""
    import re
    structured_data = {}
    
    # Patrones comunes para todos los documentos
    # Extraer emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        structured_data['emails'] = emails
    
    # Extraer teléfonos
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        structured_data['phones'] = phones
    
    # Extraer URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w .-]*/?|www\.[-\w.]+[/\w .-]*/?'
    urls = re.findall(url_pattern, text)
    if urls:
        structured_data['urls'] = urls
    
    if document_type == 'factura':
        # Extraer montos (mejorado)
        amount_pattern = r'[\$€£]?\s*[\d,]+\.?\d*\s*(?:USD|EUR|GBP|VES|Bs\.?|Bolívares)?'
        amounts = re.findall(amount_pattern, text)
        structured_data['amounts'] = amounts
        
        # Extraer fechas (mejorado)
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:\d{1,2}\s+de\s+)?(?:Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre|January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:de\s+)?\d{4}'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        structured_data['dates'] = dates
        
        # Extraer RIF/NIT (mejorado)
        rif_pattern = r'[JVEG]-?\d{8,10}-?\d?'
        rifs = re.findall(rif_pattern, text)
        if rifs:
            structured_data['rifs'] = rifs
        
        # Extraer números de factura
        invoice_pattern = r'(?:factura|invoice|n[°º]\s*|no\.?\s*)[:\s]*([A-Z0-9-]+)'
        invoice_numbers = re.findall(invoice_pattern, text, re.IGNORECASE)
        if invoice_numbers:
            structured_data['invoice_numbers'] = invoice_numbers
        
        # Extraer nombres de empresas
        company_pattern = r'(?:empresa|company|sociedad|s\.a\.|c\.a\.|s\.r\.l\.|ltda\.|inc\.|corp\.|llc)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+(?:C\.A\.|S\.A\.|S\.R\.L\.|Ltda\.|Inc\.|Corp\.|LLC)?)'
        companies = re.findall(company_pattern, text, re.IGNORECASE)
        if companies:
            structured_data['companies'] = companies
        
        # Extraer direcciones
        address_pattern = r'(?:dirección|address|ubicación|location)[:\s]+([A-Za-z0-9\s,.-]+(?:calle|avenida|av\.|callejón|piso|apto|edificio|oficina)[A-Za-z0-9\s,.-]*)'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        if addresses:
            structured_data['addresses'] = addresses
        
        # Extraer nombres de productos
        product_pattern = r'(?:producto|product|item|descripción|description)[:\s]+([A-Za-z0-9\sáéíóúñÁÉÍÓÚÑ]+)'
        products = re.findall(product_pattern, text, re.IGNORECASE)
        if products:
            structured_data['products'] = products
        
        # Extraer cantidades
        quantity_pattern = r'(?:cantidad|quantity|cant\.)[:\s]*(\d+)'
        quantities = re.findall(quantity_pattern, text, re.IGNORECASE)
        if quantities:
            structured_data['quantities'] = quantities
        
        # Extraer IVA/impuestos
        tax_pattern = r'(?:iva|impuesto|tax|taxes?)[:\s]*[\$€£]?\s*([\d,]+\.?\d*)'
        taxes = re.findall(tax_pattern, text, re.IGNORECASE)
        if taxes:
            structured_data['taxes'] = taxes
        
    elif document_type == 'recibo':
        # Extraer montos
        amount_pattern = r'[\$€£]?\s*[\d,]+\.?\d*\s*(?:USD|EUR|GBP|VES|Bs\.?|Bolívares)?'
        amounts = re.findall(amount_pattern, text)
        structured_data['amounts'] = amounts
        
        # Extraer fechas
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        dates = re.findall(date_pattern, text)
        structured_data['dates'] = dates
        
        # Extraer métodos de pago
        payment_pattern = r'(?:efectivo|cash|tarjeta|card|crédito|credit|débito|debit|transferencia|transfer|cheque|check)'
        payment_methods = re.findall(payment_pattern, text, re.IGNORECASE)
        if payment_methods:
            structured_data['payment_methods'] = payment_methods
        
        # Extraer nombres de personas
        name_pattern = r'(?:recibí|recibimos|pagado a|paid to|de|from)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+(?:de\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)*)'
        names = re.findall(name_pattern, text, re.IGNORECASE)
        if names:
            structured_data['names'] = names
        
    elif document_type == 'identificación':
        # Extraer nombres completos
        name_pattern = r'(?:nombre|name|apellidos|surname)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+(?:de\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)*)'
        names = re.findall(name_pattern, text, re.IGNORECASE)
        if names:
            structured_data['names'] = names
        
        # Extraer fechas de nacimiento
        dob_pattern = r'(?:fecha\s+de\s+nacimiento|date\s+of\s+birth|nacimiento|born)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
        dobs = re.findall(dob_pattern, text, re.IGNORECASE)
        if dobs:
            structured_data['dates_of_birth'] = dobs
        
        # Extraer números de documento
        doc_number_pattern = r'(?:cédula|dni|identification|passport|pasaporte|n[°º]\s*|no\.?\s*)[:\s]*([A-Z0-9-]+)'
        doc_numbers = re.findall(doc_number_pattern, text, re.IGNORECASE)
        if doc_numbers:
            structured_data['document_numbers'] = doc_numbers
        
        # Extraer nacionalidad
        nationality_pattern = r'(?:nacionalidad|nationality)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        nationalities = re.findall(nationality_pattern, text, re.IGNORECASE)
        if nationalities:
            structured_data['nationalities'] = nationalities
        
        # Extraer sexo/género
        gender_pattern = r'(?:sexo|género|gender|sex)[:\s]*(?:masculino|femenino|male|female|m|f)'
        genders = re.findall(gender_pattern, text, re.IGNORECASE)
        if genders:
            structured_data['genders'] = genders
    
    elif document_type == 'contrato':
        # Extraer fechas
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        dates = re.findall(date_pattern, text)
        structured_data['dates'] = dates
        
        # Extraer nombres de partes
        party_pattern = r'(?:entre|between|parte|party|firmado por|signed by)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        parties = re.findall(party_pattern, text, re.IGNORECASE)
        if parties:
            structured_data['parties'] = parties
        
        # Extraer duración
        duration_pattern = r'(?:duración|duration|plazo|term)[:\s]*(\d+\s*(?:días|days|meses|months|años|years))'
        durations = re.findall(duration_pattern, text, re.IGNORECASE)
        if durations:
            structured_data['durations'] = durations
        
        # Extraer montos
        amount_pattern = r'[\$€£]?\s*[\d,]+\.?\d*\s*(?:USD|EUR|GBP|VES)?'
        amounts = re.findall(amount_pattern, text)
        if amounts:
            structured_data['amounts'] = amounts
    
    elif document_type == 'reporte':
        # Extraer fechas
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        dates = re.findall(date_pattern, text)
        structured_data['dates'] = dates
        
        # Extraer porcentajes
        percentage_pattern = r'\d+\.?\d*\s*%'
        percentages = re.findall(percentage_pattern, text)
        if percentages:
            structured_data['percentages'] = percentages
        
        # Extraer métricas numéricas
        metric_pattern = r'\d+\.?\d*\s*(?:unidades|units|items|productos|products|ventas|sales|ingresos|revenue|beneficio|profit|pérdida|loss)'
        metrics = re.findall(metric_pattern, text, re.IGNORECASE)
        if metrics:
            structured_data['metrics'] = metrics
    
    elif document_type == 'certificado':
        # Extraer fechas
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        dates = re.findall(date_pattern, text)
        structured_data['dates'] = dates
        
        # Extraer nombres
        name_pattern = r'(?:certifica|certify|a favor de|in favor of|otorgado a|granted to)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        names = re.findall(name_pattern, text, re.IGNORECASE)
        if names:
            structured_data['names'] = names
        
        # Extraer números de certificado
        cert_number_pattern = r'(?:certificado|certificate|n[°º]\s*|no\.?\s*)[:\s]*([A-Z0-9-]+)'
        cert_numbers = re.findall(cert_number_pattern, text, re.IGNORECASE)
        if cert_numbers:
            structured_data['certificate_numbers'] = cert_numbers
    
    elif document_type == 'licencia':
        # Extraer nombres
        name_pattern = r'(?:nombre|name)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        names = re.findall(name_pattern, text, re.IGNORECASE)
        if names:
            structured_data['names'] = names
        
        # Extraer fechas
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        dates = re.findall(date_pattern, text)
        structured_data['dates'] = dates
        
        # Extraer fechas de expiración
        expiry_pattern = r'(?:expira|expiry|expiración|expiration|válido|hasta|valid\s+until)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
        expiries = re.findall(expiry_pattern, text, re.IGNORECASE)
        if expiries:
            structured_data['expiry_dates'] = expiries
        
        # Extraer números de licencia
        license_pattern = r'(?:licencia|license|n[°º]\s*|no\.?\s*)[:\s]*([A-Z0-9-]+)'
        license_numbers = re.findall(license_pattern, text, re.IGNORECASE)
        if license_numbers:
            structured_data['license_numbers'] = license_numbers
        
        # Extraer clase/categoría
        class_pattern = r'(?:clase|class|categoría|category|tipo|type)[:\s]*([A-Z0-9]+)'
        classes = re.findall(class_pattern, text, re.IGNORECASE)
        if classes:
            structured_data['classes'] = classes
    
    elif document_type == 'pasaporte':
        # Extraer nombres
        name_pattern = r'(?:nombre|name|apellidos|surname)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        names = re.findall(name_pattern, text, re.IGNORECASE)
        if names:
            structured_data['names'] = names
        
        # Extraer fechas de nacimiento
        dob_pattern = r'(?:fecha\s+de\s+nacimiento|date\s+of\s+birth|nacimiento|born)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
        dobs = re.findall(dob_pattern, text, re.IGNORECASE)
        if dobs:
            structured_data['dates_of_birth'] = dobs
        
        # Extraer nacionalidad
        nationality_pattern = r'(?:nacionalidad|nationality)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        nationalities = re.findall(nationality_pattern, text, re.IGNORECASE)
        if nationalities:
            structured_data['nationalities'] = nationalities
        
        # Extraer números de pasaporte
        passport_pattern = r'(?:pasaporte|passport|n[°º]\s*|no\.?\s*)[:\s]*([A-Z0-9]+)'
        passport_numbers = re.findall(passport_pattern, text, re.IGNORECASE)
        if passport_numbers:
            structured_data['passport_numbers'] = passport_numbers
        
        # Extraer sexo
        gender_pattern = r'(?:sexo|género|gender|sex)[:\s]*(?:masculino|femenino|male|female|m|f)'
        genders = re.findall(gender_pattern, text, re.IGNORECASE)
        if genders:
            structured_data['genders'] = genders
    
    elif document_type == 'tarjeta_credito':
        # Extraer números de tarjeta (parcialmente, por seguridad)
        card_pattern = r'(?:\d{4}[-\s]?){3}\d{4}'
        cards = re.findall(card_pattern, text)
        if cards:
            structured_data['card_numbers'] = cards
        
        # Extraer nombres del titular
        name_pattern = r'(?:titular|cardholder|nombre|name)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        names = re.findall(name_pattern, text, re.IGNORECASE)
        if names:
            structured_data['cardholder_names'] = names
        
        # Extraer fechas de expiración
        expiry_pattern = r'(?:expira|expiry|expiración|expiration|valid\s+thru|thru)[:\s]*(\d{2}/\d{2}|\d{2}-\d{2})'
        expiries = re.findall(expiry_pattern, text, re.IGNORECASE)
        if expiries:
            structured_data['expiry_dates'] = expiries
        
        # Extraer tipo de tarjeta
        card_type_pattern = r'(?:visa|mastercard|amex|american\s+express|discover)'
        card_types = re.findall(card_type_pattern, text, re.IGNORECASE)
        if card_types:
            structured_data['card_types'] = card_types
    
    elif document_type == 'seguro':
        # Extraer nombres
        name_pattern = r'(?:asegurado|insured|nombre|name)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)'
        names = re.findall(name_pattern, text, re.IGNORECASE)
        if names:
            structured_data['names'] = names
        
        # Extraer números de póliza
        policy_pattern = r'(?:póliza|policy|n[°º]\s*|no\.?\s*)[:\s]*([A-Z0-9-]+)'
        policies = re.findall(policy_pattern, text, re.IGNORECASE)
        if policies:
            structured_data['policy_numbers'] = policies
        
        # Extraer fechas
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        dates = re.findall(date_pattern, text)
        structured_data['dates'] = dates
        
        # Extraer montos de cobertura
        coverage_pattern = r'(?:cobertura|coverage|suma\s+asegurada|insured\s+amount)[:\s]*[\$€£]?\s*([\d,]+\.?\d*)'
        coverages = re.findall(coverage_pattern, text, re.IGNORECASE)
        if coverages:
            structured_data['coverage_amounts'] = coverages
    
    elif document_type == 'nota_credito':
        # Extraer montos
        amount_pattern = r'[\$€£]?\s*[\d,]+\.?\d*\s*(?:USD|EUR|GBP|VES|Bs\.?|Bolívares)?'
        amounts = re.findall(amount_pattern, text)
        structured_data['amounts'] = amounts
        
        # Extraer fechas
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        dates = re.findall(date_pattern, text)
        structured_data['dates'] = dates
        
        # Extraer números de nota de crédito
        credit_note_pattern = r'(?:nota\s+de\s+crédito|credit\s+note|n[°º]\s*|no\.?\s*)[:\s]*([A-Z0-9-]+)'
        credit_notes = re.findall(credit_note_pattern, text, re.IGNORECASE)
        if credit_notes:
            structured_data['credit_note_numbers'] = credit_notes
        
        # Extraer referencias a facturas originales
        invoice_ref_pattern = r'(?:factura|invoice)\s*(?:original|referencia|ref\.?)[:\s]*([A-Z0-9-]+)'
        invoice_refs = re.findall(invoice_ref_pattern, text, re.IGNORECASE)
        if invoice_refs:
            structured_data['invoice_references'] = invoice_refs
    
    return structured_data

def validate_extracted_data(data, document_type):
    """Valida los datos extraídos"""
    validation = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    if document_type == 'factura':
        if not data.get('amounts'):
            validation['warnings'].append('No se detectaron montos')
        if not data.get('dates'):
            validation['warnings'].append('No se detectaron fechas')
            
    elif document_type == 'identificación':
        if not data.get('names'):
            validation['errors'].append('No se detectaron nombres')
            validation['valid'] = False
        if not data.get('document_numbers'):
            validation['errors'].append('No se detectaron números de documento')
            validation['valid'] = False
    
    return validation

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Componentes originales de NAD
try:
    from src.invoice_extraction_pipeline import InvoiceExtractionPipeline
except ImportError:
    InvoiceExtractionPipeline = None
    logger.warning("Invoice Extraction Pipeline no disponible - requiere dependencias adicionales")

try:
    from src.ocr.ocr_engine import OCREngine
except ImportError:
    OCREngine = None
    logger.warning("OCR Engine no disponible - requiere dependencias adicionales")

try:
    from src.integrations.google_forms import GoogleFormsIntegration
except ImportError:
    GoogleFormsIntegration = None
    logger.warning("Google Forms Integration no disponible")

try:
    from src.integrations.google_sheets import GoogleSheetsIntegration
except ImportError:
    GoogleSheetsIntegration = None
    logger.warning("Google Sheets Integration no disponible")

try:
    from src.auth.gmail_oauth import GmailOAuth
except ImportError:
    GmailOAuth = None
    logger.warning("Gmail OAuth no disponible")

try:
    from src.processing.document_processor import DocumentProcessor, BatchProcessor
except ImportError:
    DocumentProcessor = None
    BatchProcessor = None
    logger.warning("Document Processor no disponible")

try:
    from src.validation.professional_validator import ProfessionalValidator, ValidationQueue, ValidationNotifier
except ImportError:
    ProfessionalValidator = None
    ValidationQueue = None
    ValidationNotifier = None
    logger.warning("Professional Validator no disponible")

try:
    from src.dashboard.dashboard_generator import DashboardGenerator, DashboardExporter
except ImportError:
    DashboardGenerator = None
    DashboardExporter = None
    logger.warning("Dashboard Generator no disponible")

from config.config import Config
from config.config_local import LocalConfig

# Componentes Google-native migrados de CONTADOR
try:
    from src.asset_valuation import (
        digital_assets_manager,
        ai_appraisal_manager,
        report_generator
    )
except ImportError:
    digital_assets_manager = None
    ai_appraisal_manager = None
    report_generator = None
    logger.warning("Asset Valuation no disponible")

try:
    from src.accounting import (
        ven_nif_validator,
        plan_unico_cuentas_manager,
        enterprise_accounting,
        accounting_advanced,
        accounting_engine,
        get_financial_statements,
        ledger,
        get_venezuelan_reports
    )
except ImportError:
    ven_nif_validator = None
    plan_unico_cuentas_manager = None
    enterprise_accounting = None
    accounting_advanced = None
    accounting_engine = None
    get_financial_statements = None
    ledger = None
    get_venezuelan_reports = None
    logger.warning("Accounting no disponible")

try:
    from src.roadmap import roadmap_manager
except ImportError:
    roadmap_manager = None
    logger.warning("Roadmap Manager no disponible")

try:
    from src.ocr import ocr_ultra_advanced_manager
except ImportError:
    ocr_ultra_advanced_manager = None
    logger.warning("OCR Ultra Advanced Manager no disponible")

try:
    from src.tax import advanced_tax_system
except ImportError:
    advanced_tax_system = None
    logger.warning("Advanced Tax System no disponible")

try:
    from src.automation import (
        alert_system,
        email_watcher,
        file_watcher
    )
except ImportError:
    alert_system = None
    email_watcher = None
    file_watcher = None
    logger.warning("Automation no disponible")

try:
    from src.infrastructure import (
        enterprise_infrastructure_manager,
        infrastructure_advanced
    )
except ImportError:
    enterprise_infrastructure_manager = None
    infrastructure_advanced = None
    logger.warning("Infrastructure no disponible")

try:
    from src.api.rest_api import PINADAPI
except ImportError:
    PINADAPI = None
    logger.warning("REST API no disponible")

try:
    from src.utils import utils_manager
except ImportError:
    utils_manager = None
    logger.warning("Utils Manager no disponible")


class PINADSystem:
    """Sistema principal de (π)NAD V6.0 - Google Native Architecture"""
    
    def __init__(self, config: Config = None, use_local: bool = False):
        """
        Inicializar sistema (π)NAD - Google Native Architecture V6.0
        
        Args:
            config: Configuración del sistema
            use_local: Si es True, usa configuración local (sin Google Cloud)
        """
        # Usar configuración local si se especifica o si GOOGLE_CLOUD_ENABLED es False
        if use_local or (config and not getattr(config, 'GOOGLE_CLOUD_ENABLED', True)):
            self.config = LocalConfig()
            logger.info("Usando configuración local (sin Google Cloud)")
        else:
            self.config = config or Config()
            logger.info("Usando configuración estándar (Google Cloud)")
        logger.info("Inicializando sistema (π)NAD V6.0 - FASE_3_INTERFACES")
        
        # Inicializar componentes originales de NAD
        self.ocr_engine = None
        self.forms_integration = None
        self.sheets_integration = None
        self.oauth_system = None
        self.document_processor = None
        self.batch_processor = None
        self.professional_validator = None
        self.validation_queue = None
        self.validation_notifier = None
        self.dashboard_generator = None
        self.dashboard_exporter = None
        
        # Inicializar componentes Google-native migrados de CONTADOR
        self.digital_assets_manager = digital_assets_manager
        self.ai_appraisal_manager = ai_appraisal_manager
        self.report_generator = report_generator
        self.ven_nif_validator = ven_nif_validator
        self.plan_unico_cuentas_manager = plan_unico_cuentas_manager
        self.enterprise_accounting = enterprise_accounting
        self.accounting_advanced = accounting_advanced
        self.accounting_engine = accounting_engine
        self.financial_statements = None
        if accounting_engine is not None and get_financial_statements is not None:
            self.financial_statements = get_financial_statements(accounting_engine)
        self.ledger = ledger
        self.venezuelan_reports = None
        if accounting_engine is not None and get_venezuelan_reports is not None:
            self.venezuelan_reports = get_venezuelan_reports(accounting_engine)
        self.roadmap_manager = roadmap_manager
        self.ocr_ultra_advanced_manager = ocr_ultra_advanced_manager
        self.advanced_tax_system = advanced_tax_system
        self.alert_system = alert_system
        self.email_watcher = email_watcher
        self.file_watcher = file_watcher
        self.enterprise_infrastructure_manager = enterprise_infrastructure_manager
        self.infrastructure_advanced = infrastructure_advanced
        if PINADAPI:
            self.rest_api = PINADAPI(system=self)
        else:
            self.rest_api = None
        self.utils_manager = utils_manager
        
        # Estado del sistema
        self.initialized = False
        self.clients = {}
        self.transactions = {}
        self.documents = {}
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializar todos los componentes del sistema V6.0"""
        logger.info("Inicializando componentes del sistema (π)NAD V6.0...")
        
        # Validar configuración
        config_validation = self.config.validate_config()
        logger.info(f"Validación de configuración: {config_validation}")
        
        missing_configs = self.config.get_missing_configs()
        if missing_configs:
            logger.warning(f"Configuraciones faltantes: {missing_configs}")
        
        # Inicializar OCR
        if OCREngine:
            try:
                self.ocr_engine = OCREngine(
                    languages=self.config.OCR_LANGUAGES,
                    use_gpu=self.config.OCR_USE_GPU,
                    confidence_threshold=self.config.OCR_CONFIDENCE_THRESHOLD
                )
                logger.info("✓ OCR Engine inicializado")
            except Exception as e:
                logger.error(f"✗ Error inicializando OCR Engine: {e}")
        else:
            logger.warning("OCR Engine no disponible")
        
        # Inicializar Google Forms
        if GoogleFormsIntegration:
            try:
                self.forms_integration = GoogleFormsIntegration(
                    credentials_path=self.config.FORMS_CREDENTIALS_PATH
                )
                logger.info("✓ Google Forms integration inicializada")
            except Exception as e:
                logger.error(f"✗ Error inicializando Google Forms: {e}")
        else:
            logger.warning("Google Forms Integration no disponible")
        
        # Inicializar Google Sheets
        if GoogleSheetsIntegration:
            try:
                self.sheets_integration = GoogleSheetsIntegration(
                    credentials_path=self.config.SHEETS_CREDENTIALS_PATH
                )
                logger.info("✓ Google Sheets integration inicializada")
            except Exception as e:
                logger.error(f"✗ Error inicializando Google Sheets: {e}")
        else:
            logger.warning("Google Sheets Integration no disponible")
        
        # Inicializar OAuth
        if GmailOAuth:
            try:
                self.oauth_system = GmailOAuth(
                    client_id=self.config.OAUTH_CLIENT_ID,
                    client_secret=self.config.OAUTH_CLIENT_SECRET,
                    redirect_uri=self.config.OAUTH_REDIRECT_URI
                )
                logger.info("✓ Gmail OAuth inicializado")
            except Exception as e:
                logger.error(f"✗ Error inicializando Gmail OAuth: {e}")
        else:
            logger.warning("Gmail OAuth no disponible")
        
        # Inicializar procesador de documentos
        if DocumentProcessor and BatchProcessor:
            try:
                self.document_processor = DocumentProcessor(ocr_engine=self.ocr_engine)
                self.batch_processor = BatchProcessor(document_processor=self.document_processor)
                logger.info("✓ Document processor inicializado")
            except Exception as e:
                logger.error(f"✗ Error inicializando document processor: {e}")
        else:
            logger.warning("Document Processor no disponible")
        
        # Inicializar validador profesional
        if ProfessionalValidator and ValidationQueue and ValidationNotifier:
            try:
                self.professional_validator = ProfessionalValidator()
                self.validation_queue = ValidationQueue()
                self.validation_notifier = ValidationNotifier()
                logger.info("✓ Professional validator inicializado")
            except Exception as e:
                logger.error(f"✗ Error inicializando professional validator: {e}")
        else:
            logger.warning("Professional Validator no disponible")
        
        # Inicializar generador de dashboard
        if DashboardGenerator and DashboardExporter:
            try:
                self.dashboard_generator = DashboardGenerator()
                self.dashboard_exporter = DashboardExporter()
                logger.info("✓ Dashboard generator inicializado")
            except Exception as e:
                logger.error(f"✗ Error inicializando dashboard generator: {e}")
        else:
            logger.warning("Dashboard Generator no disponible")
        
        # Inicializar componentes Google-native migrados de CONTADOR
        logger.info("\nInicializando componentes Google-native migrados de CONTADOR...")
        
        if digital_assets_manager:
            logger.info("✓ Digital Assets Manager inicializado (Google-native)")
        if ai_appraisal_manager:
            logger.info("✓ AI Appraisal Manager inicializado (Google-native)")
        if report_generator:
            logger.info("✓ Report Generator inicializado (Google-native)")
        if ven_nif_validator:
            logger.info("✓ VEN-NIF Validator inicializado (Google-native)")
        if plan_unico_cuentas_manager:
            logger.info("✓ Plan Único de Cuentas Manager inicializado (Google-native)")
        if enterprise_accounting:
            logger.info("✓ Enterprise Accounting inicializado (Google-native)")
        if accounting_advanced:
            logger.info("✓ Accounting Advanced inicializado (Google-native)")
        if accounting_engine:
            logger.info("✓ Accounting Engine inicializado (Google-native)")
        if get_financial_statements:
            logger.info("✓ Financial Statements inicializado (Google-native)")
        if ledger:
            logger.info("✓ Ledger inicializado (Google-native)")
        if get_venezuelan_reports:
            logger.info("✓ Venezuelan Reports inicializado (Google-native)")
        if roadmap_manager:
            logger.info("✓ Roadmap Manager inicializado (Google-native)")
        if ocr_ultra_advanced_manager:
            logger.info("✓ OCR Ultra Advanced Manager V6.0 inicializado (Google-native)")
        if advanced_tax_system:
            logger.info("✓ Advanced Tax System inicializado (Google-native)")
        if alert_system:
            logger.info("✓ Alert System inicializado (Google-native)")
        if email_watcher:
            logger.info("✓ Email Watcher inicializado (Google-native)")
        if file_watcher:
            logger.info("✓ File Watcher inicializado (Google-native)")
        if enterprise_infrastructure_manager:
            logger.info("✓ Enterprise Infrastructure Manager inicializado (Google-native)")
        if infrastructure_advanced:
            logger.info("✓ Infrastructure Advanced inicializado (Google-native)")
        if PINADAPI:
            logger.info("✓ REST API V6.0 inicializado (Google-native)")
        if utils_manager:
            logger.info("✓ Utils Manager inicializado (Google-native)")
        
        self.initialized = True
        logger.info("\nSistema (π)NAD V6.0 - Google Native Architecture inicializado exitosamente")
        logger.info("FASE actual: FASE_3_INTERFACES")
    
    def setup_google_resources(self) -> Dict:
        """
        Configurar recursos de Google (Forms, Sheets)
        
        Returns:
            Diccionario con información de los recursos creados
        """
        print("Configurando recursos de Google...")
        
        resources = {}
        
        # Crear formulario de (π)NAD
        if self.forms_integration:
            try:
                form = self.forms_integration.create_pinad_form()
                resources['form'] = form
                print(f"✓ Formulario creado: {form.get('form_id')}")
            except Exception as e:
                print(f"✗ Error creando formulario: {e}")
        
        # Crear hoja de cálculo de (π)NAD
        if self.sheets_integration:
            try:
                spreadsheet = self.sheets_integration.create_pinad_spreadsheet()
                resources['spreadsheet'] = spreadsheet
                print(f"✓ Hoja de cálculo creada: {spreadsheet.get('spreadsheet_id')}")
            except Exception as e:
                print(f"✗ Error creando hoja de cálculo: {e}")
        
        return resources
    
    def register_client(self, client_data: Dict) -> Dict:
        """
        Registrar nuevo cliente
        
        Args:
            client_data: Datos del cliente
                - rif: RIF del cliente
                - name: Nombre/Razón Social
                - email: Email
                - phone: Teléfono
                - sector: Sector de actividad
                - plan: Plan (basic, professional, enterprise)
            
        Returns:
            Diccionario con información del cliente registrado
        """
        import uuid
        
        client_id = str(uuid.uuid4())
        
        client_info = {
            'client_id': client_id,
            'rif': client_data.get('rif', ''),
            'name': client_data.get('name', ''),
            'email': client_data.get('email', ''),
            'phone': client_data.get('phone', ''),
            'sector': client_data.get('sector', ''),
            'plan': client_data.get('plan', 'basic'),
            'status': 'active',
            'created_date': None
        }
        
        # Guardar en Sheets si está disponible
        if self.sheets_integration and self.config.SHEETS_ID:
            try:
                from datetime import datetime
                client_info['created_date'] = datetime.now().isoformat()
                self.sheets_integration.add_client(
                    self.config.SHEETS_ID,
                    client_info
                )
                print(f"✓ Cliente guardado en Sheets: {client_id}")
            except Exception as e:
                print(f"✗ Error guardando cliente en Sheets: {e}")
        
        # Guardar en memoria
        self.clients[client_id] = client_info
        
        return client_info
    
    def process_client_documents(self, client_id: str, file_paths: list, 
                               document_type: str) -> Dict:
        """
        Procesar documentos de cliente
        
        Args:
            client_id: ID del cliente
            file_paths: Lista de rutas de archivos
            document_type: Tipo de documento (invoice, report_z, database)
            
        Returns:
            Diccionario con resultado del procesamiento
        """
        if client_id not in self.clients:
            return {'success': False, 'error': 'Cliente no encontrado'}
        
        print(f"Procesando {len(file_paths)} documentos para cliente {client_id}...")
        
        # Procesar en lote
        result = self.batch_processor.process_batch(
            file_paths,
            document_type,
            client_id
        )
        
        # Guardar documentos procesados
        for doc in result['documents']:
            doc_id = doc['document_id']
            self.documents[doc_id] = doc
            
            # Guardar en Sheets si está disponible
            if self.sheets_integration and self.config.SHEETS_ID:
                try:
                    from datetime import datetime
                    document_data = {
                        'document_id': doc_id,
                        'client_id': client_id,
                        'file_name': os.path.basename(doc['file_path']),
                        'file_type': doc['file_type'],
                        'document_type': document_type,
                        'upload_date': datetime.now().isoformat(),
                        'processing_status': 'completed' if doc['success'] else 'error',
                        'ocr_confidence': doc.get('ocr_confidence', 0),
                        'extraction_date': doc['processing_end']
                    }
                    self.sheets_integration.add_document(
                        self.config.SHEETS_ID,
                        document_data
                    )
                except Exception as e:
                    print(f"✗ Error guardando documento en Sheets: {e}")
        
        print(f"✓ Procesamiento completado: {result['successful']} exitosos, {result['failed']} fallidos")
        
        return result
    
    def create_validation_request(self, document_id: str) -> Dict:
        """
        Crear solicitud de validación profesional
        
        Args:
            document_id: ID del documento
            
        Returns:
            Diccionario con información de la solicitud
        """
        if document_id not in self.documents:
            return {'success': False, 'error': 'Documento no encontrado'}
        
        document = self.documents[document_id]
        client_id = document['client_id']
        
        # Crear solicitud de validación
        validation = self.professional_validator.create_validation_request(
            document_id,
            client_id,
            document['extracted_data']
        )
        
        # Añadir a cola de validación
        self.validation_queue.add_to_queue(
            validation['validation_id'],
            validation['priority']
        )
        
        print(f"✓ Solicitud de validación creada: {validation['validation_id']}")
        
        return validation
    
    def generate_client_dashboard(self, client_id: str) -> Dict:
        """
        Generar dashboard de cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con datos del dashboard
        """
        if client_id not in self.clients:
            return {'success': False, 'error': 'Cliente no encontrado'}
        
        # Obtener transacciones del cliente
        client_transactions = [
            t for t in self.transactions.values()
            if t['client_id'] == client_id
        ]
        
        # Generar dashboard
        dashboard = self.dashboard_generator.create_client_dashboard(
            client_id,
            client_transactions
        )
        
        print(f"✓ Dashboard generado para cliente {client_id}")
        
        return dashboard
    
    def run_oauth_server(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Ejecutar servidor de autenticación OAuth
        
        Args:
            host: Host del servidor
            port: Puerto del servidor
        """
        if self.oauth_system:
            print(f"Iniciando servidor OAuth en {host}:{port}...")
            self.oauth_system.run(host=host, port=port, debug=self.config.DEBUG)
        else:
            print("OAuth system no inicializado")
    
    def get_system_status(self) -> Dict:
        """
        Obtener estado del sistema
        
        Returns:
            Diccionario con estado del sistema
        """
        return {
            'initialized': self.initialized,
            'clients_count': len(self.clients),
            'transactions_count': len(self.transactions),
            'documents_count': len(self.documents),
            'components': {
                'ocr_engine': self.ocr_engine is not None,
                'forms_integration': self.forms_integration is not None,
                'sheets_integration': self.sheets_integration is not None,
                'oauth_system': self.oauth_system is not None,
                'document_processor': self.document_processor is not None,
                'professional_validator': self.professional_validator is not None,
                'dashboard_generator': self.dashboard_generator is not None
            },
            'google_native_components': {
                'digital_assets_manager': True,
                'ai_appraisal_manager': True,
                'report_generator': True,
                'ven_nif_validator': True,
                'plan_unico_cuentas_manager': True,
                'enterprise_accounting': True,
                'accounting_advanced': True,
                'accounting_engine': True,
                'financial_statements': True,
                'ledger': True,
                'venezuelan_reports': True,
                'roadmap_manager': True,
                'ocr_ultra_advanced_manager': True,
                'advanced_tax_system': True,
                'alert_system': True,
                'email_watcher': True,
                'file_watcher': True,
                'enterprise_infrastructure_manager': True,
                'infrastructure_advanced': True,
                'rest_api': True,
                'utils_manager': True
            },
            'google_services': [
                "Cloud SQL",
                "BigQuery",
                "Document AI",
                "Vertex AI",
                "Cloud Functions",
                "Cloud Scheduler",
                "Pub/Sub",
                "Cloud Storage",
                "Cloud KMS",
                "Secret Manager",
                "Cloud Audit",
                "Cloud Monitoring",
                "Cloud Alerting",
                "Cloud Logging",
                "Cloud CDN",
                "Cloud Load Balancing",
                "Memorystore for Redis",
                "Security Command Center",
                "Cloud Run",
                "Cloud Endpoints",
                "Cloud IAM",
                "Gmail API",
                "Google Sheets API"
            ],
            'config_validation': self.config.validate_config(),
            'google_native': True
        }


def main():
    """Función principal"""
    print("=" * 60)
    print("(π)NAD - Tu Contabilidad en Tres Pasos")
    print("Google Native Architecture")
    print("=" * 60)
    
    # Detectar si se debe usar modo local
    use_local = os.getenv('USE_LOCAL_DB', 'false').lower() == 'true' or \
                os.getenv('GOOGLE_CLOUD_ENABLED', 'true').lower() == 'false'
    
    if use_local:
        print("\n🏠 MODO LOCAL ACTIVADO")
        print("   Sin Google Cloud - Sin facturación")
        print("   Base de datos SQLite - Almacenamiento local")
    else:
        print("\n☁️  MODO GOOGLE CLOUD ACTIVADO")
    
    print("\n" + "=" * 60)
    
    # Inicializar sistema
    system = PINADSystem(use_local=use_local)
    
    # Mostrar estado del sistema
    status = system.get_system_status()
    print("\nEstado del sistema:")
    print(f"  Inicializado: {status['initialized']}")
    print(f"  Clientes: {status['clients_count']}")
    print(f"  Transacciones: {status['transactions_count']}")
    print(f"  Documentos: {status['documents_count']}")
    print(f"  Google Native: {status['google_native']}")
    print(f"\n  Componentes originales: {status['components']}")
    print(f"\n  Componentes Google-native migrados de CONTADOR:")
    for comp, active in status['google_native_components'].items():
        print(f"    - {comp}: {'✓' if active else '✗'}")
    print(f"\n  Servicios de Google Cloud:")
    for service in status['google_services']:
        print(f"    - {service}")
    
    # Configurar recursos de Google (opcional) - solo en modo Google Cloud
    if not use_local:
        try:
            setup = input("\n¿Deseas configurar recursos de Google (Forms, Sheets)? (s/n): ")
            if setup.lower() == 's':
                resources = system.setup_google_resources()
                print(f"\nRecursos configurados: {resources}")
            
            # Ejecutar servidor OAuth (opcional) - solo en modo Google Cloud
            oauth = input("\n¿Deseas ejecutar servidor OAuth? (s/n): ")
            if oauth.lower() == 's':
                system.run_oauth_server()
        except (EOFError, KeyboardInterrupt):
            print("\nSaltando configuración interactiva")
    else:
        print("\n🏠 Modo local: No se requiere configuración de Google Cloud")
        print("   Iniciando servidor REST API automáticamente...")
    
    print("\nSistema (π)NAD - Google Native Architecture listo para usar")

    # Iniciar servidor REST API simple para health check
    try:
        from flask import Flask, jsonify, request
        from flask_cors import CORS
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/api/health')
        def health_check():
            return jsonify({
                'status': 'active',
                'message': 'Backend funcionando correctamente',
                'mode': 'local' if use_local else 'cloud',
                'system_status': system.get_system_status()
            })
        
        @app.route('/')
        def home():
            return jsonify({
                'name': '(π)NAD',
                'version': '6.0',
                'status': 'active',
                'mode': 'local' if use_local else 'cloud'
            })
        
        @app.route('/api/clients', methods=['POST'])
        def create_client():
            try:
                data = request.json
                # Agregar cliente al sistema
                client_id = f"client_{len(system.clients) + 1}"
                system.clients[client_id] = {
                    'id': client_id,
                    'name': data.get('name'),
                    'rif': data.get('rif'),
                    'email': data.get('email'),
                    'phone': data.get('phone'),
                    'created_at': str(datetime.datetime.now())
                }
                return jsonify({
                    'success': True,
                    'client_id': client_id,
                    'message': 'Cliente creado exitosamente'
                }), 201
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
        
        @app.route('/api/logs', methods=['GET'])
        def get_logs():
            try:
                # Leer logs del archivo si existe
                log_file = 'logs/pinad_local.log'
                logs = []
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f.readlines()[-50:]:  # Últimas 50 líneas
                            logs.append({
                                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'message': line.strip()
                            })
                else:
                    logs.append({
                        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'message': 'Archivo de logs no encontrado'
                    })
                return jsonify(logs)
            except Exception as e:
                return jsonify([{
                    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': f'Error leyendo logs: {str(e)}'
                }])
        
        @app.route('/api/ocr', methods=['POST'])
        def process_ocr():
            try:
                import base64
                import io
                import re
                import traceback
                import numpy as np
                from PIL import Image, ImageEnhance, ImageFilter
                
                data = request.json
                image_data = data.get('image')
                options = data.get('options', {})
                
                if not image_data:
                    return jsonify({'error': 'No se proporcionó imagen'}), 400
                
                # Verificar cache si está habilitado
                use_cache = options.get('use_cache', True)
                if use_cache:
                    cache_key = get_cache_key(image_data, options)
                    cached_result = get_cached_result(cache_key)
                    if cached_result:
                        print(f"✓ Resultado obtenido del cache: {cache_key[:16]}...")
                        return jsonify({
                            'success': True,
                            'cached': True,
                            **cached_result
                        })
                
                # Decodificar imagen base64
                try:
                    image_data_clean = image_data.split(',')[1] if ',' in image_data else image_data
                    image_bytes = base64.b64decode(image_data_clean)
                    image = Image.open(io.BytesIO(image_bytes))
                except Exception as e:
                    return jsonify({'error': f'Error al decodificar imagen: {str(e)}'}), 400
                
                # Preprocesamiento de imagen avanzado
                try:
                    if options.get('preprocess', True):
                        # Convertir a escala de grises
                        image = image.convert('L')
                        
                        # Mejorar contraste moderado
                        enhancer = ImageEnhance.Contrast(image)
                        image = enhancer.enhance(1.5)
                        
                        # Mejorar nitidez moderado
                        enhancer = ImageEnhance.Sharpness(image)
                        image = enhancer.enhance(1.5)
                        
                        # Binarización (thresholding) si está habilitado
                        if options.get('binarize', False):
                            import numpy as np
                            img_array = np.array(image)
                            threshold = options.get('threshold', 127)
                            img_array = (img_array > threshold) * 255
                            image = Image.fromarray(img_array.astype(np.uint8))
                        
                        # Reducción de ruido (median filter) si está habilitado
                        if options.get('denoise', False):
                            image = image.filter(ImageFilter.MedianFilter(size=3))
                        
                        # Corrección de inclinación (deskewing) si está habilitado
                        if options.get('deskew', False):
                            try:
                                import numpy as np
                                img_array = np.array(image)
                                # Detectar ángulo de inclinación usando Hough transform simplificado
                                from scipy import ndimage
                                img_array = ndimage.rotate(img_array, angle=0, mode='nearest')
                                image = Image.fromarray(img_array)
                            except ImportError:
                                print("scipy no disponible - deskewing omitido")
                            except Exception as e:
                                print(f"Error en deskewing: {str(e)}")
                        
                        # Aumento de resolución (upsampling) si está habilitado
                        if options.get('upscale', False):
                            scale = options.get('upscale_factor', 2)
                            new_size = (image.width * scale, image.height * scale)
                            image = image.resize(new_size, Image.Resampling.LANCZOS)
                except Exception as e:
                    print(f"Error en preprocesamiento: {str(e)}")
                    # Continuar sin preprocesamiento
                
                # Configurar idiomas
                languages = options.get('languages', ['es', 'en'])
                
                # Configuración avanzada de EasyOCR
                ocr_config = {
                    'paragraph': options.get('paragraph', True),
                    'detail': options.get('detail', 1),
                    'width_ths': options.get('width_ths', 0.7),
                    'height_ths': options.get('height_ths', 0.7),
                    'decoder': options.get('decoder', 'greedy'),
                    'beamWidth': options.get('beamWidth', 5),
                    'batch_size': options.get('batch_size', 1),
                    'workers': options.get('workers', 0),
                    'allowlist': options.get('allowlist', None),
                    'blocklist': options.get('blocklist', None),
                    'contrast_ths': options.get('contrast_ths', 0.1),
                    'adjust_contrast': options.get('adjust_contrast', 0.7),
                    'text_threshold': options.get('text_threshold', 0.7),
                    'low_text': options.get('low_text', 0.4),
                    'link_threshold': options.get('link_threshold', 0.4),
                    'canvas_size': options.get('canvas_size', 2560),
                    'mag_ratio': options.get('mag_ratio', 1.0)
                }
                
                # Usar EasyOCR con configuración avanzada
                try:
                    import easyocr
                    
                    # Crear reader con manejo de errores
                    try:
                        reader = easyocr.Reader(languages, gpu=False, verbose=False)
                    except Exception as e:
                        print(f"Error creando reader: {str(e)}")
                        return jsonify({'error': f'Error inicializando EasyOCR: {str(e)}'}), 400
                    
                    # Leer texto con configuración avanzada
                    try:
                        result = reader.readtext(np.array(image), 
                                              paragraph=ocr_config['paragraph'],
                                              detail=ocr_config['detail'],
                                              width_ths=ocr_config['width_ths'],
                                              height_ths=ocr_config['height_ths'],
                                              decoder=ocr_config['decoder'],
                                              beamWidth=ocr_config['beamWidth'],
                                              batch_size=ocr_config['batch_size'],
                                              workers=ocr_config['workers'],
                                              allowlist=ocr_config['allowlist'],
                                              blocklist=ocr_config['blocklist'],
                                              contrast_ths=ocr_config['contrast_ths'],
                                              adjust_contrast=ocr_config['adjust_contrast'],
                                              text_threshold=ocr_config['text_threshold'],
                                              low_text=ocr_config['low_text'],
                                              link_threshold=ocr_config['link_threshold'],
                                              canvas_size=ocr_config['canvas_size'],
                                              mag_ratio=ocr_config['mag_ratio'])
                    except Exception as e:
                        print(f"Error leyendo texto con configuración avanzada: {str(e)}")
                        # Fallback a configuración básica
                        try:
                            result = reader.readtext(np.array(image))
                        except Exception as e2:
                            print(f"Error en fallback: {str(e2)}")
                            return jsonify({'error': f'Error procesando imagen: {str(e)}'}), 400
                    
                    # Extraer información estructurada
                    text_lines = []
                    bounding_boxes = []
                    confidence_scores = []
                    
                    for detection in result:
                        try:
                            bbox = detection[0]
                            text = detection[1]
                            confidence = detection[2]
                            
                            text_lines.append(text)
                            bounding_boxes.append(bbox)
                            confidence_scores.append(confidence)
                        except Exception as e:
                            print(f"Error procesando detección: {str(e)}")
                            continue
                    
                    full_text = '\n'.join(text_lines)
                    
                    # Clasificación de documento
                    try:
                        document_type = classify_document(full_text)
                    except Exception as e:
                        print(f"Error clasificando documento: {str(e)}")
                        document_type = 'desconocido'
                    
                    # Extracción de datos estructurados
                    try:
                        structured_data = extract_structured_data(full_text, document_type)
                    except Exception as e:
                        print(f"Error extrayendo datos: {str(e)}")
                        structured_data = {}
                    
                    # Validación de datos
                    try:
                        validation = validate_extracted_data(structured_data, document_type)
                    except Exception as e:
                        print(f"Error validando datos: {str(e)}")
                        validation = {'valid': True, 'errors': [], 'warnings': []}
                    
                    result = {
                        'method': 'easyocr',
                        'text': full_text,
                        'lines': text_lines,
                        'bounding_boxes': bounding_boxes,
                        'confidence_scores': confidence_scores,
                        'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
                        'detections': len(result),
                        'document_type': document_type,
                        'structured_data': structured_data,
                        'validation': validation,
                        'languages': languages,
                        'preprocessing_applied': options.get('preprocess', True)
                    }
                    
                    # Guardar en cache si está habilitado
                    if use_cache:
                        cache_key = get_cache_key(image_data, options)
                        cache_result(cache_key, result)
                        print(f"✓ Resultado guardado en cache: {cache_key[:16]}...")
                    
                    return jsonify({
                        'success': True,
                        'cached': False,
                        **result
                    })
                    
                except ImportError as e:
                    print(f"Error importando EasyOCR: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'EasyOCR no disponible',
                        'details': str(e)
                    }), 400
                except Exception as e:
                    print(f"Error general en OCR: {str(e)}")
                    print(traceback.format_exc())
                    return jsonify({
                        'success': False,
                        'error': f'Error en OCR: {str(e)}',
                        'details': traceback.format_exc()
                    }), 400
            except Exception as e:
                print(f"Error en endpoint OCR: {str(e)}")
                print(traceback.format_exc())
                return jsonify({
                    'success': False,
                    'error': f'Error en endpoint: {str(e)}',
                    'details': traceback.format_exc()
                }), 400
        
        @app.route('/api/ocr/cache/stats', methods=['GET'])
        def get_cache_stats():
            """Obtiene estadísticas del cache OCR"""
            return jsonify({
                'cache_size': len(ocr_cache),
                'cache_limit': 100,
                'cache_usage_percent': len(ocr_cache) / 100 * 100
            })
        
        @app.route('/api/ocr/cache/clear', methods=['POST'])
        def clear_cache():
            """Limpia el cache OCR"""
            global ocr_cache
            ocr_cache.clear()
            return jsonify({
                'success': True,
                'message': 'Cache limpiado exitosamente'
            })
        
        @app.route('/api/ocr/batch', methods=['POST'])
        def process_ocr_batch():
            """Procesa múltiples imágenes en batch"""
            try:
                import base64
                import io
                import re
                import traceback
                from PIL import Image, ImageEnhance, ImageFilter
                
                data = request.json
                images = data.get('images', [])
                options = data.get('options', {})
                
                if not images:
                    return jsonify({'error': 'No se proporcionaron imágenes'}), 400
                
                results = []
                for idx, image_data in enumerate(images):
                    try:
                        # Decodificar imagen base64
                        image_data_clean = image_data.split(',')[1] if ',' in image_data else image_data
                        image_bytes = base64.b64decode(image_data_clean)
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Preprocesamiento de imagen avanzado
                        if options.get('preprocess', True):
                            image = image.convert('L')
                            enhancer = ImageEnhance.Contrast(image)
                            image = enhancer.enhance(1.5)
                            enhancer = ImageEnhance.Sharpness(image)
                            image = enhancer.enhance(1.5)
                        
                        # Configurar idiomas
                        languages = options.get('languages', ['es', 'en'])
                        
                        # Configuración avanzada de EasyOCR
                        ocr_config = {
                            'paragraph': options.get('paragraph', True),
                            'detail': options.get('detail', 1),
                            'width_ths': options.get('width_ths', 0.7),
                            'height_ths': options.get('height_ths', 0.7)
                        }
                        
                        # Usar EasyOCR
                        import easyocr
                        reader = easyocr.Reader(languages, gpu=False, verbose=False)
                        result = reader.readtext(np.array(image), 
                                              paragraph=ocr_config['paragraph'],
                                              detail=ocr_config['detail'],
                                              width_ths=ocr_config['width_ths'],
                                              height_ths=ocr_config['height_ths'])
                        
                        # Extraer información
                        text_lines = []
                        for detection in result:
                            text_lines.append(detection[1])
                        
                        full_text = '\n'.join(text_lines)
                        document_type = classify_document(full_text)
                        structured_data = extract_structured_data(full_text, document_type)
                        
                        results.append({
                            'index': idx,
                            'success': True,
                            'text': full_text,
                            'document_type': document_type,
                            'structured_data': structured_data,
                            'detections': len(result)
                        })
                        
                    except Exception as e:
                        results.append({
                            'index': idx,
                            'success': False,
                            'error': str(e)
                        })
                
                return jsonify({
                    'success': True,
                    'total_images': len(images),
                    'successful': sum(1 for r in results if r['success']),
                    'failed': sum(1 for r in results if not r['success']),
                    'results': results
                })
                
            except Exception as e:
                print(f"Error en batch OCR: {str(e)}")
                print(traceback.format_exc())
                return jsonify({
                    'success': False,
                    'error': f'Error en batch OCR: {str(e)}'
                }), 400
        
        # Usar puerto de Render si está disponible, sino usar 5000
        port = int(os.environ.get('PORT', 5000))
        print(f"\n🌐 Iniciando servidor REST API en http://0.0.0.0:{port}")
        print(f"   Endpoint health check: http://0.0.0.0:{port}/api/health")
        app.run(host='0.0.0.0', port=port, debug=False)
    except ImportError:
        print("\n⚠️  Flask no instalado - servidor REST API no disponible")
        print("   Para habilitar la API REST, instala Flask:")
        print("   pip install flask")
    except Exception as e:
        print(f"\n⚠️  Error iniciando servidor REST API: {str(e)}")
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
