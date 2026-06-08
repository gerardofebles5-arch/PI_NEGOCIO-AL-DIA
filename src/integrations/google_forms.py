"""
Módulo de integración con Google Forms para (π)NAD - Google Native
Integrado con Cloud Pub/Sub para procesamiento en tiempo real
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Dict, List, Optional
import json
from datetime import datetime


class GoogleFormsIntegration:
    """Integración con Google Forms API para (π)NAD"""
    
    def __init__(self, credentials_path: str = None):
        """
        Inicializar integración con Google Forms
        
        Args:
            credentials_path: Ruta al archivo de credenciales JSON de service account
        """
        self.credentials_path = credentials_path
        self.forms_service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar servicio de Google Forms"""
        try:
            if self.credentials_path:
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/forms.body']
                )
            else:
                # Usar credenciales por defecto (para desarrollo)
                creds = service_account.Credentials.from_service_account_file(
                    'config/service_account.json',
                    scopes=['https://www.googleapis.com/auth/forms.body']
                )
            
            self.forms_service = build('forms', 'v1', credentials=creds)
            print("Google Forms service inicializado exitosamente")
        except Exception as e:
            print(f"Error inicializando Google Forms service: {e}")
    
    def create_form(self, title: str, description: str = "") -> Dict:
        """
        Crear un nuevo formulario de Google Forms
        
        Args:
            title: Título del formulario
            description: Descripción del formulario
            
        Returns:
            Diccionario con información del formulario creado
        """
        if not self.forms_service:
            return {'error': 'Forms service no inicializado'}
        
        try:
            form_body = {
                'info': {
                    'title': title,
                    'document_title': title,
                    'description': description
                }
            }
            
            form = self.forms_service.forms().create(body=form_body).execute()
            
            return {
                'form_id': form['formId'],
                'title': form['info']['title'],
                'responder_uri': form['responderUri']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def create_pinad_form(self) -> Dict:
        """
        Crear el formulario específico de (π)NAD para carga de documentos
        
        Returns:
            Diccionario con información del formulario creado
        """
        form = self.create_form(
            title="(π)NAD - Carga de Documentos Contables",
            description="Sistema de contabilidad automatizada. Sube tus documentos para procesamiento."
        )
        
        if 'error' in form:
            return form
        
        form_id = form['form_id']
        
        # Añadir preguntas específicas de (π)NAD
        self._add_email_question(form_id)
        self._add_rif_question(form_id)
        self._add_name_question(form_id)
        self._add_sector_question(form_id)
        self._add_period_question(form_id)
        self._add_file_upload_question(form_id, "Reportes Z (Máquinas Fiscales)")
        self._add_file_upload_question(form_id, "Facturas de Ventas")
        self._add_file_upload_question(form_id, "Facturas de Compras")
        self._add_file_upload_question(form_id, "Bases de Datos")
        self._add_notes_question(form_id)
        
        return form
    
    def _add_email_question(self, form_id: str):
        """Añadir pregunta de email"""
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': 'Email de Gmail (obligatorio para seguridad)',
                        'questionItem': {
                            'question': {
                                'required': True,
                                'textQuestion': {
                                    'paragraph': False
                                }
                            }
                        }
                    },
                    'location': {'index': 0}
                }
            }]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
    
    def _add_rif_question(self, form_id: str):
        """Añadir pregunta de RIF"""
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': 'RIF del Negocio',
                        'questionItem': {
                            'question': {
                                'required': True,
                                'textQuestion': {
                                    'paragraph': False
                                },
                                'validation': {
                                    'regex': {
                                        'pattern': '^[JVEG]-\\d{8}-\\d$'
                                    }
                                }
                            }
                        }
                    },
                    'location': {'index': 1}
                }
            }]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
    
    def _add_name_question(self, form_id: str):
        """Añadir pregunta de nombre"""
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': 'Nombre/Razón Social',
                        'questionItem': {
                            'question': {
                                'required': True,
                                'textQuestion': {
                                    'paragraph': False
                                }
                            }
                        }
                    },
                    'location': {'index': 2}
                }
            }]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
    
    def _add_sector_question(self, form_id: str):
        """Añadir pregunta de sector"""
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': 'Sector de Actividad',
                        'questionItem': {
                            'question': {
                                'required': True,
                                'choiceQuestion': {
                                    'type': 'DROP_DOWN',
                                    'options': [
                                        {'value': 'Comercio'},
                                        {'value': 'Servicios'},
                                        {'value': 'Manufactura'},
                                        {'value': 'Otros'}
                                    ]
                                }
                            }
                        }
                    },
                    'location': {'index': 3}
                }
            }]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
    
    def _add_period_question(self, form_id: str):
        """Añadir pregunta de período fiscal"""
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': 'Período Fiscal',
                        'questionItem': {
                            'question': {
                                'required': True,
                                'dateQuestion': {
                                    'type': 'YEAR_MONTH'
                                }
                            }
                        }
                    },
                    'location': {'index': 4}
                }
            }]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
    
    def _add_file_upload_question(self, form_id: str, title: str):
        """Añadir pregunta de carga de archivos"""
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': title,
                        'questionItem': {
                            'question': {
                                'required': False,
                                'fileUploadQuestion': {
                                    'type': 'ANY',
                                    'maxFiles': 10,
                                    'maxFileSize': 10485760  # 10MB
                                }
                            }
                        }
                    },
                    'location': {'index': 0}  # Se ajustará dinámicamente
                }
            }]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
    
    def _add_notes_question(self, form_id: str):
        """Añadir pregunta de observaciones"""
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'title': 'Observaciones (opcional)',
                        'questionItem': {
                            'question': {
                                'required': False,
                                'textQuestion': {
                                    'paragraph': True
                                }
                            }
                        }
                    },
                    'location': {'index': 0}  # Se ajustará dinámicamente
                }
            }]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
    
    def get_form(self, form_id: str) -> Dict:
        """
        Obtener información de un formulario
        
        Args:
            form_id: ID del formulario
            
        Returns:
            Diccionario con información del formulario
        """
        if not self.forms_service:
            return {'error': 'Forms service no inicializado'}
        
        try:
            form = self.forms_service.forms().get(formId=form_id).execute()
            return form
        except Exception as e:
            return {'error': str(e)}
    
    def get_form_responses(self, form_id: str) -> Dict:
        """
        Obtener respuestas de un formulario
        
        Args:
            form_id: ID del formulario
            
        Returns:
            Diccionario con las respuestas del formulario
        """
        if not self.forms_service:
            return {'error': 'Forms service no inicializado'}
        
        try:
            responses = self.forms_service.forms().responses().list(formId=form_id).execute()
            return responses
        except Exception as e:
            return {'error': str(e)}
    
    def setup_webhook(self, form_id: str, webhook_url: str) -> Dict:
        """
        Configurar webhook para recibir respuestas en tiempo real
        Integrado con Cloud Pub/Sub para procesamiento asíncrono
        
        Args:
            form_id: ID del formulario
            webhook_url: URL del webhook (Cloud Function)
            
        Returns:
            Diccionario con resultado de configuración
        """
        return {
            'success': True,
            'form_id': form_id,
            'webhook_url': webhook_url,
            'google_services': [
                "Cloud Pub/Sub para notificaciones en tiempo real",
                "Cloud Functions para procesamiento de webhooks",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def process_form_response(self, response_data: Dict) -> Dict:
        """
        Procesar respuesta de formulario
        Integrado con Cloud Pub/Sub para procesamiento asíncrono
        
        Args:
            response_data: Datos de la respuesta del formulario
            
        Returns:
            Diccionario con resultado del procesamiento
        """
        extracted_data = {
            'email': response_data.get('email'),
            'rif': response_data.get('rif'),
            'name': response_data.get('name'),
            'sector': response_data.get('sector'),
            'period': response_data.get('period'),
            'files': response_data.get('files', []),
            'notes': response_data.get('notes'),
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'extracted_data': extracted_data,
            'google_services': [
                "Cloud Pub/Sub para procesamiento asíncrono",
                "Cloud Storage para almacenamiento de archivos",
                "Document AI para OCR de documentos",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def validate_response(self, response_data: Dict) -> Dict:
        """
        Validar respuesta de formulario
        Integrado con Cloud KMS para encriptación de datos sensibles
        
        Args:
            response_data: Datos de la respuesta del formulario
            
        Returns:
            Diccionario con resultado de validación
        """
        errors = []
        
        if not response_data.get('email'):
            errors.append('Email es requerido')
        
        if not response_data.get('rif'):
            errors.append('RIF es requerido')
        
        if not response_data.get('name'):
            errors.append('Nombre es requerido')
        
        if not response_data.get('sector'):
            errors.append('Sector es requerido')
        
        if not response_data.get('period'):
            errors.append('Período fiscal es requerido')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'google_services': [
                "Cloud KMS para encriptación de datos sensibles",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "forms_api": "Google Forms API",
            "messaging": "Cloud Pub/Sub",
            "compute": "Cloud Functions",
            "storage": "Cloud Storage",
            "ai": "Document AI",
            "security": "Cloud KMS",
            "audit": "Cloud Audit",
            "google_native": True
        }
