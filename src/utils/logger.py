"""
Sistema de logging para (π)NAD
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


class PINADLogger:
    """Sistema de logging para (π)NAD"""
    
    def __init__(self, name: str = 'pinad', log_level: str = 'INFO', 
                 log_file: str = 'logs/pinad.log'):
        """
        Inicializar logger
        
        Args:
            name: Nombre del logger
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Ruta del archivo de log
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Crear directorio de logs si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # JSON formatter para producción
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler con rotación
        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, extra: dict = None):
        """Log mensaje DEBUG"""
        self.logger.debug(message, extra=extra or {})
    
    def info(self, message: str, extra: dict = None):
        """Log mensaje INFO"""
        self.logger.info(message, extra=extra or {})
    
    def warning(self, message: str, extra: dict = None):
        """Log mensaje WARNING"""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: dict = None, exc_info: bool = False):
        """Log mensaje ERROR"""
        self.logger.error(message, extra=extra or {}, exc_info=exc_info)
    
    def critical(self, message: str, extra: dict = None, exc_info: bool = False):
        """Log mensaje CRITICAL"""
        self.logger.critical(message, extra=extra or {}, exc_info=exc_info)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       response_time: float, user_id: str = None):
        """Log request de API"""
        self.info(
            f"API Request: {method} {endpoint} - Status: {status_code} - Time: {response_time}ms",
            extra={
                'type': 'api_request',
                'method': method,
                'endpoint': endpoint,
                'status_code': status_code,
                'response_time_ms': response_time,
                'user_id': user_id
            }
        )
    
    def log_document_processing(self, document_id: str, client_id: str, 
                               status: str, processing_time: float):
        """Log procesamiento de documento"""
        self.info(
            f"Document Processing: {document_id} - Client: {client_id} - Status: {status} - Time: {processing_time}s",
            extra={
                'type': 'document_processing',
                'document_id': document_id,
                'client_id': client_id,
                'status': status,
                'processing_time_seconds': processing_time
            }
        )
    
    def log_validation(self, validation_id: str, validator_id: str, 
                      action: str, client_id: str = None):
        """Log validación"""
        self.info(
            f"Validation: {validation_id} - Validator: {validator_id} - Action: {action}",
            extra={
                'type': 'validation',
                'validation_id': validation_id,
                'validator_id': validator_id,
                'action': action,
                'client_id': client_id
            }
        )
    
    def log_error_with_context(self, error: Exception, context: dict = None):
        """Log error con contexto"""
        self.error(
            f"Error: {str(error)}",
            extra={
                'type': 'error',
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context or {}
            },
            exc_info=True
        )


def get_logger(name: str = 'pinad', log_level: str = 'INFO', 
               log_file: str = 'logs/pinad.log') -> PINADLogger:
    """
    Factory function para obtener logger
    
    Args:
        name: Nombre del logger
        log_level: Nivel de logging
        log_file: Ruta del archivo de log
        
    Returns:
        Instancia de PINADLogger
    """
    return PINADLogger(name, log_level, log_file)
