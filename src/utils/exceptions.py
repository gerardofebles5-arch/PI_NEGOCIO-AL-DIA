"""
Excepciones personalizadas para (π)NAD
"""

from typing import Optional, Dict, Any


class PINADException(Exception):
    """Excepción base para (π)NAD"""
    
    def __init__(self, message: str, error_code: str = None, 
                 details: Dict[str, Any] = None):
        """
        Inicializar excepción
        
        Args:
            message: Mensaje de error
            error_code: Código de error
            details: Detalles adicionales del error
        """
        self.message = message
        self.error_code = error_code or 'PINAD_ERROR'
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir excepción a diccionario"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }


class OCRException(PINADException):
    """Excepción relacionada con OCR"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code='OCR_ERROR', details=details)


class DocumentProcessingException(PINADException):
    """Excepción relacionada con procesamiento de documentos"""
    
    def __init__(self, message: str, document_id: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if document_id:
            details['document_id'] = document_id
        super().__init__(message, error_code='DOC_PROCESSING_ERROR', details=details)


class ValidationException(PINADException):
    """Excepción relacionada con validación"""
    
    def __init__(self, message: str, validation_id: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if validation_id:
            details['validation_id'] = validation_id
        super().__init__(message, error_code='VALIDATION_ERROR', details=details)


class ClientException(PINADException):
    """Excepción relacionada con clientes"""
    
    def __init__(self, message: str, client_id: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if client_id:
            details['client_id'] = client_id
        super().__init__(message, error_code='CLIENT_ERROR', details=details)


class GoogleIntegrationException(PINADException):
    """Excepción relacionada con integraciones de Google"""
    
    def __init__(self, message: str, service: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if service:
            details['service'] = service
        super().__init__(message, error_code='GOOGLE_INTEGRATION_ERROR', details=details)


class AuthenticationException(PINADException):
    """Excepción relacionada con autenticación"""
    
    def __init__(self, message: str, user_id: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if user_id:
            details['user_id'] = user_id
        super().__init__(message, error_code='AUTH_ERROR', details=details)


class DashboardException(PINADException):
    """Excepción relacionada con dashboards"""
    
    def __init__(self, message: str, client_id: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if client_id:
            details['client_id'] = client_id
        super().__init__(message, error_code='DASHBOARD_ERROR', details=details)


class ConfigurationException(PINADException):
    """Excepción relacionada con configuración"""
    
    def __init__(self, message: str, config_key: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if config_key:
            details['config_key'] = config_key
        super().__init__(message, error_code='CONFIG_ERROR', details=details)


class FileException(PINADException):
    """Excepción relacionada con archivos"""
    
    def __init__(self, message: str, file_path: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if file_path:
            details['file_path'] = file_path
        super().__init__(message, error_code='FILE_ERROR', details=details)


class APIException(PINADException):
    """Excepción relacionada con API"""
    
    def __init__(self, message: str, status_code: int = 500, 
                 endpoint: str = None, details: Dict[str, Any] = None):
        details = details or {}
        details['status_code'] = status_code
        if endpoint:
            details['endpoint'] = endpoint
        super().__init__(message, error_code='API_ERROR', details=details)


class ValidatorException(PINADException):
    """Excepción relacionada con validadores"""
    
    def __init__(self, message: str, validator_id: str = None, 
                 details: Dict[str, Any] = None):
        details = details or {}
        if validator_id:
            details['validator_id'] = validator_id
        super().__init__(message, error_code='VALIDATOR_ERROR', details=details)


class ErrorHandler:
    """Manejador de errores para (π)NAD"""
    
    def __init__(self, logger=None):
        """
        Inicializar manejador de errores
        
        Args:
            logger: Instancia de logger
        """
        self.logger = logger
    
    def handle_exception(self, exception: Exception, context: Dict = None) -> Dict:
        """
        Manejar excepción y retornar respuesta estandarizada
        
        Args:
            exception: Excepción a manejar
            context: Contexto adicional
            
        Returns:
            Diccionario con respuesta estandarizada
        """
        context = context or {}
        
        if isinstance(exception, PINADException):
            # Excepción personalizada de (π)NAD
            error_response = {
                'success': False,
                'error': exception.to_dict()
            }
            
            if self.logger:
                self.logger.error_with_context(exception, context)
            
            return error_response
        else:
            # Excepción genérica
            error_response = {
                'success': False,
                'error': {
                    'error_code': 'INTERNAL_ERROR',
                    'message': str(exception),
                    'details': context
                }
            }
            
            if self.logger:
                self.logger.error_with_context(exception, context)
            
            return error_response
    
    def raise_and_handle(self, exception_type, message: str, **kwargs):
        """
        Lanzar excepción y manejarla
        
        Args:
            exception_type: Tipo de excepción
            message: Mensaje de error
            **kwargs: Argumentos adicionales para la excepción
            
        Returns:
            Diccionario con respuesta estandarizada
        """
        try:
            raise exception_type(message, **kwargs)
        except Exception as e:
            return self.handle_exception(e)
