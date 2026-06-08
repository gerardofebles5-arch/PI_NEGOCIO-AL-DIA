"""
Servicio de Base de Datos - Conexión con Supabase
Obtiene datos reales de documentos y transacciones
"""
import os
from supabase import create_client

class DatabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://rteuftlsbglpgcawsdqz.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_KEY", "sb_publishable_eUlKRfeFNvqdURtW_abbIA_N8Qte0l3")
        self.client = create_client(self.supabase_url, self.supabase_key)
    
    def get_documents(self, limit=10):
        """Obtener documentos reales de la base de datos"""
        try:
            response = self.client.table('documents').select('*').order('created_at', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo documentos: {e}")
            return []
    
    def get_metrics(self):
        """Calcular métricas reales basadas en datos"""
        try:
            # Obtener todos los documentos
            documents = self.client.table('documents').select('*').execute()
            docs = documents.data
            
            # Calcular métricas
            total_docs = len(docs)
            completed = len([d for d in docs if d.get('status') == 'completed'])
            in_progress = len([d for d in docs if d.get('status') == 'processing'])
            pending = len([d for d in docs if d.get('status') == 'pending'])
            error = len([d for d in docs if d.get('status') == 'error'])
            
            # Calcular transacciones
            total_transactions = sum([d.get('transaction_count', 0) for d in docs])
            
            # Calcular alertas
            alerts = len([d for d in docs if d.get('needs_attention', False)])
            
            return {
                "total_documents": total_docs,
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "error": error,
                "total_transactions": total_transactions,
                "alerts": alerts
            }
        except Exception as e:
            print(f"Error calculando métricas: {e}")
            return {
                "total_documents": 0,
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "error": 0,
                "total_transactions": 0,
                "alerts": 0
            }
    
    def save_document(self, document_data):
        """Guardar documento en la base de datos"""
        try:
            response = self.client.table('documents').insert(document_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error guardando documento: {e}")
            return None
    
    def save_ocr_results(self, document_id, ocr_result):
        """Guardar resultados completos del OCR en la base de datos"""
        try:
            # Guardar items/transacciones
            if ocr_result.get('items'):
                for item in ocr_result['items']:
                    self.client.table('transactions').insert({
                        'document_id': document_id,
                        'description': item.get('description', ''),
                        'quantity': item.get('quantity', 1),
                        'unit_price': item.get('unit_price', 0),
                        'amount': item.get('amount', 0),
                        'type': 'item'
                    }).execute()
            
            # Guardar tablas extraídas
            if ocr_result.get('tablas'):
                for i, tabla in enumerate(ocr_result['tablas']):
                    self.client.table('extracted_tables').insert({
                        'document_id': document_id,
                        'table_index': i,
                        'table_data': tabla,
                        'row_count': len(tabla) if isinstance(tabla, list) else 0,
                        'column_count': len(tabla[0]) if isinstance(tabla, list) and len(tabla) > 0 else 0
                    }).execute()
            
            # Guardar firmas
            if ocr_result.get('firmas'):
                for firma in ocr_result['firmas']:
                    self.client.table('signatures').insert({
                        'document_id': document_id,
                        'location': firma.get('location', ''),
                        'confidence': firma.get('confidence', 0),
                        'bounding_box': firma.get('bounding_box', {})
                    }).execute()
            
            # Guardar códigos QR
            if ocr_result.get('codigos_qr'):
                for qr in ocr_result['codigos_qr']:
                    self.client.table('qr_codes').insert({
                        'document_id': document_id,
                        'qr_data': qr.get('data', ''),
                        'location': qr.get('location', ''),
                        'confidence': qr.get('confidence', 0)
                    }).execute()
            
            # Guardar códigos de barras
            if ocr_result.get('codigos_barras'):
                for barcode in ocr_result['codigos_barras']:
                    self.client.table('barcodes').insert({
                        'document_id': document_id,
                        'barcode_data': barcode.get('data', ''),
                        'barcode_type': barcode.get('type', ''),
                        'location': barcode.get('location', ''),
                        'confidence': barcode.get('confidence', 0)
                    }).execute()
            
            # Actualizar documento con contadores
            self.client.table('documents').update({
                'tables_count': len(ocr_result.get('tablas', [])),
                'signatures_count': len(ocr_result.get('firmas', [])),
                'qr_codes_count': len(ocr_result.get('codigos_qr', [])),
                'barcodes_count': len(ocr_result.get('codigos_barras', [])),
                'transaction_count': len(ocr_result.get('items', [])),
                'status': 'completed'
            }).eq('id', document_id).execute()
            
            return True
        except Exception as e:
            print(f"Error guardando resultados OCR: {e}")
            return False
    
    def get_transactions(self, document_id=None):
        """Obtener transacciones reales"""
        try:
            if document_id:
                response = self.client.table('transactions').select('*').eq('document_id', document_id).execute()
            else:
                response = self.client.table('transactions').select('*').order('created_at', desc=True).limit(50).execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo transacciones: {e}")
            return []
    
    def get_reports(self, report_type='iva'):
        """Obtener datos para reportes"""
        try:
            if report_type == 'iva':
                # Calcular IVA real
                transactions = self.client.table('transactions').select('*').execute()
                trans = transactions.data
                
                ventas_gravadas = sum([t.get('amount', 0) for t in trans if t.get('type') == 'sale'])
                compras_gravadas = sum([t.get('amount', 0) for t in trans if t.get('type') == 'purchase'])
                iva_debito = ventas_gravadas * 0.16
                iva_credito = compras_gravadas * 0.16
                iva_pagar = iva_debito - iva_credito
                
                return {
                    "Ventas Gravadas": ventas_gravadas,
                    "Compras Gravadas": compras_gravadas,
                    "IVA Débito Fiscal": iva_debito,
                    "IVA Crédito Fiscal": iva_credito,
                    "IVA a Pagar": iva_pagar
                }
            elif report_type == 'islr':
                # Calcular ISLR real
                transactions = self.client.table('transactions').select('*').execute()
                trans = transactions.data
                
                ingresos_brutos = sum([t.get('amount', 0) for t in trans if t.get('type') == 'income'])
                deducciones = sum([t.get('amount', 0) for t in trans if t.get('type') == 'deduction'])
                ingreso_neto = ingresos_brutos - deducciones
                islr = ingreso_neto * 0.15
                
                return {
                    "Ingresos Brutos": ingresos_brutos,
                    "Deducciones Permitidas": deducciones,
                    "Ingreso Neto": ingreso_neto,
                    "ISLR Calculado": islr
                }
        except Exception as e:
            print(f"Error obteniendo reporte: {e}")
            return {}
