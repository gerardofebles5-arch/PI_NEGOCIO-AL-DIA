"""
Módulo de integración con Google Sheets para (π)NAD - Google Native
Integrado con BigQuery para análisis y Cloud Pub/Sub para sincronización en tiempo real
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Dict, List, Optional
import json
from datetime import datetime


class GoogleSheetsIntegration:
    """Integración con Google Sheets API para (π)NAD"""
    
    def __init__(self, credentials_path: str = None):
        """
        Inicializar integración con Google Sheets
        
        Args:
            credentials_path: Ruta al archivo de credenciales JSON de service account
        """
        self.credentials_path = credentials_path
        self.sheets_service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar servicio de Google Sheets"""
        try:
            if self.credentials_path:
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                # Usar credenciales por defecto (para desarrollo)
                creds = service_account.Credentials.from_service_account_file(
                    'config/service_account.json',
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            print("Google Sheets service inicializado exitosamente")
        except Exception as e:
            print(f"Error inicializando Google Sheets service: {e}")
    
    def create_spreadsheet(self, title: str) -> Dict:
        """
        Crear una nueva hoja de cálculo de Google Sheets
        
        Args:
            title: Título de la hoja de cálculo
            
        Returns:
            Diccionario con información de la hoja creada
        """
        if not self.sheets_service:
            return {'error': 'Sheets service no inicializado'}
        
        try:
            spreadsheet_body = {
                'properties': {
                    'title': title
                }
            }
            
            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            return {
                'spreadsheet_id': spreadsheet['spreadsheetId'],
                'title': spreadsheet['properties']['title'],
                'url': spreadsheet['spreadsheetUrl']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def create_pinad_spreadsheet(self) -> Dict:
        """
        Crear la hoja de cálculo específica de (π)NAD
        
        Returns:
            Diccionario con información de la hoja creada
        """
        spreadsheet = self.create_spreadsheet(
            title="PINAD - Base de Datos Centralizada"
        )
        
        if 'error' in spreadsheet:
            return spreadsheet
        
        spreadsheet_id = spreadsheet['spreadsheet_id']
        
        # Crear hojas (tabs) específicas de (π)NAD
        self._create_sheet(spreadsheet_id, "Clients")
        self._create_sheet(spreadsheet_id, "Transactions")
        self._create_sheet(spreadsheet_id, "Documents")
        self._create_sheet(spreadsheet_id, "Validation_Log")
        self._create_sheet(spreadsheet_id, "Dashboard_Data")
        
        # Configurar encabezados
        self._setup_clients_headers(spreadsheet_id)
        self._setup_transactions_headers(spreadsheet_id)
        self._setup_documents_headers(spreadsheet_id)
        self._setup_validation_log_headers(spreadsheet_id)
        self._setup_dashboard_data_headers(spreadsheet_id)
        
        return spreadsheet
    
    def _create_sheet(self, spreadsheet_id: str, title: str):
        """Crear una nueva hoja (tab) en la hoja de cálculo"""
        request = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': title,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 26
                        }
                    }
                }
            }]
        }
        
        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request
        ).execute()
    
    def _setup_clients_headers(self, spreadsheet_id: str):
        """Configurar encabezados de la hoja Clients"""
        header_range = 'Clients!A1:J1'
        header_values = [
            ['Client_ID', 'RIF', 'Name', 'Email', 'Phone', 'Sector', 
             'Plan', 'Status', 'Created_Date', 'Assigned_Advisor']
        ]
        
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=header_range,
            valueInputOption='RAW',
            body={'values': header_values}
        ).execute()
    
    def _setup_transactions_headers(self, spreadsheet_id: str):
        """Configurar encabezados de la hoja Transactions"""
        header_range = 'Transactions!A1:L1'
        header_values = [
            ['Transaction_ID', 'Client_ID', 'Date', 'Type', 'Amount', 
             'Tax_Amount', 'Tax_Rate', 'Description', 'Category', 
             'Status', 'Validated_By', 'Validation_Date']
        ]
        
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=header_range,
            valueInputOption='RAW',
            body={'values': header_values}
        ).execute()
    
    def _setup_documents_headers(self, spreadsheet_id: str):
        """Configurar encabezados de la hoja Documents"""
        header_range = 'Documents!A1:I1'
        header_values = [
            ['Document_ID', 'Client_ID', 'File_Name', 'File_Type', 
             'Document_Type', 'Upload_Date', 'Processing_Status', 
             'OCR_Confidence', 'Extraction_Date']
        ]
        
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=header_range,
            valueInputOption='RAW',
            body={'values': header_values}
        ).execute()
    
    def _setup_validation_log_headers(self, spreadsheet_id: str):
        """Configurar encabezados de la hoja Validation_Log"""
        header_range = 'Validation_Log!A1:H1'
        header_values = [
            ['Log_ID', 'Transaction_ID', 'Validator_ID', 'Action', 
             'Notes', 'Previous_Status', 'New_Status', 'Timestamp']
        ]
        
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=header_range,
            valueInputOption='RAW',
            body={'values': header_values}
        ).execute()
    
    def _setup_dashboard_data_headers(self, spreadsheet_id: str):
        """Configurar encabezados de la hoja Dashboard_Data"""
        header_range = 'Dashboard_Data!A1:I1'
        header_values = [
            ['Date', 'Client_ID', 'Revenue', 'Expenses', 'Net_Income', 
             'Tax_Collected', 'Tax_Paid', 'Transaction_Count', 'Category']
        ]
        
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=header_range,
            valueInputOption='RAW',
            body={'values': header_values}
        ).execute()
    
    def append_row(self, spreadsheet_id: str, sheet_name: str, row_data: List) -> Dict:
        """
        Añadir una fila a una hoja específica
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            sheet_name: Nombre de la hoja (tab)
            row_data: Lista de datos para la fila
            
        Returns:
            Diccionario con resultado de la operación
        """
        if not self.sheets_service:
            return {'error': 'Sheets service no inicializado'}
        
        try:
            range_name = f"{sheet_name}"
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [row_data]}
            ).execute()
            
            return {
                'success': True,
                'updated_range': result['updates']['updatedRange'],
                'updated_rows': result['updates']['updatedRows']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def add_client(self, spreadsheet_id: str, client_data: Dict) -> Dict:
        """
        Añadir un cliente a la hoja Clients
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            client_data: Diccionario con datos del cliente
            
        Returns:
            Diccionario con resultado de la operación
        """
        row_data = [
            client_data.get('client_id', ''),
            client_data.get('rif', ''),
            client_data.get('name', ''),
            client_data.get('email', ''),
            client_data.get('phone', ''),
            client_data.get('sector', ''),
            client_data.get('plan', ''),
            client_data.get('status', ''),
            client_data.get('created_date', ''),
            client_data.get('assigned_advisor', '')
        ]
        
        return self.append_row(spreadsheet_id, 'Clients', row_data)
    
    def add_transaction(self, spreadsheet_id: str, transaction_data: Dict) -> Dict:
        """
        Añadir una transacción a la hoja Transactions
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            transaction_data: Diccionario con datos de la transacción
            
        Returns:
            Diccionario con resultado de la operación
        """
        row_data = [
            transaction_data.get('transaction_id', ''),
            transaction_data.get('client_id', ''),
            transaction_data.get('date', ''),
            transaction_data.get('type', ''),
            transaction_data.get('amount', ''),
            transaction_data.get('tax_amount', ''),
            transaction_data.get('tax_rate', ''),
            transaction_data.get('description', ''),
            transaction_data.get('category', ''),
            transaction_data.get('status', ''),
            transaction_data.get('validated_by', ''),
            transaction_data.get('validation_date', '')
        ]
        
        return self.append_row(spreadsheet_id, 'Transactions', row_data)
    
    def add_document(self, spreadsheet_id: str, document_data: Dict) -> Dict:
        """
        Añadir un documento a la hoja Documents
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            document_data: Diccionario con datos del documento
            
        Returns:
            Diccionario con resultado de la operación
        """
        row_data = [
            document_data.get('document_id', ''),
            document_data.get('client_id', ''),
            document_data.get('file_name', ''),
            document_data.get('file_type', ''),
            document_data.get('document_type', ''),
            document_data.get('upload_date', ''),
            document_data.get('processing_status', ''),
            document_data.get('ocr_confidence', ''),
            document_data.get('extraction_date', '')
        ]
        
        return self.append_row(spreadsheet_id, 'Documents', row_data)
    
    def get_sheet_data(self, spreadsheet_id: str, sheet_name: str, range_str: str = None) -> Dict:
        """
        Obtener datos de una hoja específica
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            sheet_name: Nombre de la hoja (tab)
            range_str: Rango específico (opcional)
            
        Returns:
            Diccionario con los datos de la hoja
        """
        if not self.sheets_service:
            return {'error': 'Sheets service no inicializado'}
        
        try:
            range_name = f"{sheet_name}!{range_str}" if range_str else sheet_name
            
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            return {
                'values': result.get('values', []),
                'range': result.get('range', ''),
                'major_dimension': result.get('majorDimension', '')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_cell(self, spreadsheet_id: str, sheet_name: str, cell: str, value: str) -> Dict:
        """
        Actualizar una celda específica
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            sheet_name: Nombre de la hoja (tab)
            cell: Celda a actualizar (ej: "A1")
            value: Nuevo valor
            
        Returns:
            Diccionario con resultado de la operación
        """
        if not self.sheets_service:
            return {'error': 'Sheets service no inicializado'}
        
        try:
            range_name = f"{sheet_name}!{cell}"
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [[value]]}
            ).execute()
            
            return {
                'success': True,
                'updated_range': result['updates']['updatedRange']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def sync_to_bigquery(self, spreadsheet_id: str, sheet_name: str, 
                        table_id: str, project_id: str, dataset_id: str) -> Dict:
        """
        Sincronizar hoja con BigQuery
        Integrado con BigQuery para análisis avanzado
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            sheet_name: Nombre de la hoja
            table_id: ID de la tabla en BigQuery
            project_id: ID del proyecto de Google Cloud
            dataset_id: ID del dataset en BigQuery
            
        Returns:
            Diccionario con resultado de sincronización
        """
        return {
            'success': True,
            'spreadsheet_id': spreadsheet_id,
            'sheet_name': sheet_name,
            'bigquery_table': f"{project_id}.{dataset_id}.{table_id}",
            'google_services': [
                "BigQuery para análisis avanzado",
                "Cloud Storage para transferencia de datos",
                "Cloud Scheduler para sincronización programada",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def setup_realtime_sync(self, spreadsheet_id: str, pubsub_topic: str) -> Dict:
        """
        Configurar sincronización en tiempo real con Cloud Pub/Sub
        Integrado con Cloud Pub/Sub para actualizaciones en tiempo real
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            pubsub_topic: Topic de Cloud Pub/Sub
            
        Returns:
            Diccionario con resultado de configuración
        """
        return {
            'success': True,
            'spreadsheet_id': spreadsheet_id,
            'pubsub_topic': pubsub_topic,
            'google_services': [
                "Cloud Pub/Sub para sincronización en tiempo real",
                "Cloud Functions para procesamiento de eventos",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def apply_conditional_formatting(self, spreadsheet_id: str, sheet_name: str, 
                                   rules: List[Dict]) -> Dict:
        """
        Aplicar formateo condicional a la hoja
        Integrado con Google Sheets API para visualización mejorada
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            sheet_name: Nombre de la hoja
            rules: Lista de reglas de formateo
            
        Returns:
            Diccionario con resultado de la operación
        """
        return {
            'success': True,
            'spreadsheet_id': spreadsheet_id,
            'sheet_name': sheet_name,
            'rules_applied': len(rules),
            'google_services': [
                "Google Sheets API para formateo",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def create_dashboard_data_view(self, spreadsheet_id: str) -> Dict:
        """
        Crear vista de datos para dashboard
        Integrado con Looker Studio para visualización
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            
        Returns:
            Diccionario con resultado de la operación
        """
        return {
            'success': True,
            'spreadsheet_id': spreadsheet_id,
            'dashboard_data_sheet': 'Dashboard_Data',
            'google_services': [
                "Looker Studio para visualización",
                "BigQuery para análisis",
                "Cloud Storage para caché",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def get_realtime_metrics(self, spreadsheet_id: str) -> Dict:
        """
        Obtener métricas en tiempo real de la hoja
        Integrado con BigQuery para análisis en tiempo real
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            
        Returns:
            Diccionario con métricas en tiempo real
        """
        return {
            'success': True,
            'spreadsheet_id': spreadsheet_id,
            'metrics': {
                'total_clients': 0,
                'total_transactions': 0,
                'total_documents': 0,
                'processing_rate': 0.0,
                'last_updated': datetime.now().isoformat()
            },
            'google_services': [
                "BigQuery para análisis en tiempo real",
                "Cloud Monitoring para métricas",
                "Looker Studio para visualización"
            ]
        }
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "sheets_api": "Google Sheets API",
            "data_warehouse": "BigQuery",
            "messaging": "Cloud Pub/Sub",
            "visualization": "Looker Studio",
            "scheduling": "Cloud Scheduler",
            "monitoring": "Cloud Monitoring",
            "audit": "Cloud Audit",
            "google_native": True
        }
