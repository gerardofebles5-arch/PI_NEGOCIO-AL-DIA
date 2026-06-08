"""
Módulo de procesamiento de documentos con OCR para (π)NAD
"""

from src.ocr.ocr_engine import OCREngine
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import os


class DocumentProcessor:
    """Procesador de documentos con OCR para (π)NAD"""
    
    def __init__(self, ocr_engine: OCREngine = None):
        """
        Inicializar procesador de documentos
        
        Args:
            ocr_engine: Instancia del motor OCR
        """
        self.ocr_engine = ocr_engine or OCREngine()
        self.processed_documents = {}
    
    def process_document(self, file_path: str, document_type: str, 
                        client_id: str) -> Dict:
        """
        Procesar documento con OCR
        
        Args:
            file_path: Ruta del archivo a procesar
            document_type: Tipo de documento (invoice, report_z, database)
            client_id: ID del cliente
            
        Returns:
            Diccionario con resultado del procesamiento
        """
        document_id = str(uuid.uuid4())
        processing_start = datetime.now()
        
        # Determinar tipo de archivo
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Procesar según tipo de archivo
        if file_extension == '.pdf':
            result = self._process_pdf(file_path, document_type)
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            result = self._process_image(file_path, document_type)
        elif file_extension in ['.xlsx', '.xls', '.csv']:
            result = self._process_spreadsheet(file_path, document_type)
        else:
            result = {
                'success': False,
                'error': f'Tipo de archivo no soportado: {file_extension}'
            }
        
        processing_end = datetime.now()
        processing_time = (processing_end - processing_start).total_seconds()
        
        # Guardar resultado
        document_result = {
            'document_id': document_id,
            'client_id': client_id,
            'file_path': file_path,
            'document_type': document_type,
            'file_type': file_extension,
            'processing_start': processing_start.isoformat(),
            'processing_end': processing_end.isoformat(),
            'processing_time_seconds': processing_time,
            'success': result.get('success', False),
            'extracted_data': result.get('extracted_data', {}),
            'ocr_confidence': result.get('ocr_confidence', 0.0),
            'error': result.get('error', None)
        }
        
        self.processed_documents[document_id] = document_result
        
        return document_result
    
    def _process_image(self, file_path: str, document_type: str) -> Dict:
        """Procesar imagen con OCR"""
        try:
            if document_type == 'invoice':
                extracted_data = self.ocr_engine.extract_invoice_data(file_path)
            elif document_type == 'report_z':
                extracted_data = self.ocr_engine.extract_report_z_data(file_path)
            else:
                # Extracción genérica
                text = self.ocr_engine.extract_text_only(file_path)
                extracted_data = {'raw_text': text}
            
            # Calcular confianza promedio
            ocr_results = self.ocr_engine.extract_text_with_confidence(file_path)
            if ocr_results:
                avg_confidence = sum(r['confidence'] for r in ocr_results) / len(ocr_results)
            else:
                avg_confidence = 0.0
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'ocr_confidence': avg_confidence
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_pdf(self, file_path: str, document_type: str) -> Dict:
        """Procesar PDF con OCR"""
        try:
            page_texts = self.ocr_engine.extract_from_pdf(file_path)
            
            if not page_texts:
                return {
                    'success': False,
                    'error': 'No se pudo extraer texto del PDF'
                }
            
            # Combinar texto de todas las páginas
            combined_text = '\n\n'.join(page_texts)
            
            # Extraer datos según tipo de documento
            if document_type == 'invoice':
                # Para facturas, procesar cada página y combinar resultados
                extracted_data = {'raw_text': combined_text}
                # Aquí se podría implementar lógica más avanzada
            elif document_type == 'report_z':
                extracted_data = {'raw_text': combined_text}
            else:
                extracted_data = {'raw_text': combined_text}
            
            # Calcular confianza (estimada para PDF)
            ocr_confidence = 0.85  # Valor estimado para PDFs
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'ocr_confidence': ocr_confidence,
                'page_count': len(page_texts)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_spreadsheet(self, file_path: str, document_type: str) -> Dict:
        """Procesar hoja de cálculo (sin OCR, lectura directa)"""
        try:
            import pandas as pd
            
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Convertir a diccionario
            extracted_data = {
                'data': df.to_dict('records'),
                'columns': list(df.columns),
                'row_count': len(df),
                'column_count': len(df.columns)
            }
            
            # Para bases de datos, no hay OCR
            ocr_confidence = 1.0
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'ocr_confidence': ocr_confidence
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_processed_document(self, document_id: str) -> Optional[Dict]:
        """
        Obtener documento procesado por ID
        
        Args:
            document_id: ID del documento
            
        Returns:
            Datos del documento procesado o None
        """
        return self.processed_documents.get(document_id)
    
    def get_client_documents(self, client_id: str) -> List[Dict]:
        """
        Obtener todos los documentos procesados de un cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Lista de documentos procesados
        """
        return [
            doc for doc in self.processed_documents.values()
            if doc['client_id'] == client_id
        ]
    
    def validate_extracted_data(self, document_id: str) -> Dict:
        """
        Validar datos extraídos de documento
        
        Args:
            document_id: ID del documento
            
        Returns:
            Diccionario con resultado de validación
        """
        document = self.get_processed_document(document_id)
        if not document:
            return {'success': False, 'error': 'Documento no encontrado'}
        
        extracted_data = document['extracted_data']
        validation_result = {
            'document_id': document_id,
            'validation_date': datetime.now().isoformat(),
            'validations': []
        }
        
        # Validaciones según tipo de documento
        if document['document_type'] == 'invoice':
            validation_result['validations'].extend(
                self._validate_invoice_data(extracted_data)
            )
        elif document['document_type'] == 'report_z':
            validation_result['validations'].extend(
                self._validate_report_z_data(extracted_data)
            )
        
        # Calcular puntuación de validación
        total_validations = len(validation_result['validations'])
        passed_validations = sum(1 for v in validation_result['validations'] if v['passed'])
        validation_score = passed_validations / total_validations if total_validations > 0 else 0.0
        
        validation_result['validation_score'] = validation_score
        validation_result['passed'] = validation_score >= 0.7
        
        return validation_result
    
    def _validate_invoice_data(self, data: Dict) -> List[Dict]:
        """Validar datos de factura"""
        validations = []
        
        # Validar número de factura
        if data.get('invoice_number'):
            validations.append({
                'field': 'invoice_number',
                'passed': True,
                'message': 'Número de factura presente'
            })
        else:
            validations.append({
                'field': 'invoice_number',
                'passed': False,
                'message': 'Número de factura no encontrado'
            })
        
        # Validar RIF
        if data.get('rif'):
            validations.append({
                'field': 'rif',
                'passed': True,
                'message': 'RIF presente'
            })
        else:
            validations.append({
                'field': 'rif',
                'passed': False,
                'message': 'RIF no encontrado'
            })
        
        # Validar fecha
        if data.get('date'):
            validations.append({
                'field': 'date',
                'passed': True,
                'message': 'Fecha presente'
            })
        else:
            validations.append({
                'field': 'date',
                'passed': False,
                'message': 'Fecha no encontrada'
            })
        
        # Validar monto total
        if data.get('total'):
            validations.append({
                'field': 'total',
                'passed': True,
                'message': 'Monto total presente'
            })
        else:
            validations.append({
                'field': 'total',
                'passed': False,
                'message': 'Monto total no encontrado'
            })
        
        return validations
    
    def _validate_report_z_data(self, data: Dict) -> List[Dict]:
        """Validar datos de Reporte Z"""
        validations = []
        
        # Validar fecha del reporte
        if data.get('report_date'):
            validations.append({
                'field': 'report_date',
                'passed': True,
                'message': 'Fecha del reporte presente'
            })
        else:
            validations.append({
                'field': 'report_date',
                'passed': False,
                'message': 'Fecha del reporte no encontrada'
            })
        
        # Validar ventas totales
        if data.get('total_sales'):
            validations.append({
                'field': 'total_sales',
                'passed': True,
                'message': 'Ventas totales presentes'
            })
        else:
            validations.append({
                'field': 'total_sales',
                'passed': False,
                'message': 'Ventas totales no encontradas'
            })
        
        # Validar impuesto total
        if data.get('total_tax'):
            validations.append({
                'field': 'total_tax',
                'passed': True,
                'message': 'Impuesto total presente'
            })
        else:
            validations.append({
                'field': 'total_tax',
                'passed': False,
                'message': 'Impuesto total no encontrado'
            })
        
        return validations


class BatchProcessor:
    """Procesador por lotes para múltiples documentos"""
    
    def __init__(self, document_processor: DocumentProcessor):
        """
        Inicializar procesador por lotes
        
        Args:
            document_processor: Instancia del procesador de documentos
        """
        self.document_processor = document_processor
    
    def process_batch(self, file_paths: List[str], document_type: str, 
                     client_id: str) -> Dict:
        """
        Procesar múltiples documentos en lote
        
        Args:
            file_paths: Lista de rutas de archivos
            document_type: Tipo de documento
            client_id: ID del cliente
            
        Returns:
            Diccionario con resultados del procesamiento por lotes
        """
        results = {
            'total_files': len(file_paths),
            'successful': 0,
            'failed': 0,
            'documents': []
        }
        
        for file_path in file_paths:
            result = self.document_processor.process_document(
                file_path, document_type, client_id
            )
            
            results['documents'].append(result)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        return results
