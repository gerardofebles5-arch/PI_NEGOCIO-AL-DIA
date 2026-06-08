"""
Structured Logger para (π)NAD V6.0
Logging estructurado con JSON, niveles de log y contexto
"""

import logging
import json
import sys
from typing import Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from contextvars import ContextVar

# Contexto de log global
_log_context: ContextVar[Dict[str, Any]] = ContextVar('log_context', default={})


class LogLevel(Enum):
    """Niveles de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """
    Logger estructurado con salida JSON
    Implementa logging estructurado para mejor análisis
    """
    
    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        enable_console: bool = True,
        enable_file: bool = True,
        log_file: Optional[str] = None,
        include_timestamp: bool = True,
        include_context: bool = True,
    ):
        """
        Inicializar logger estructurado
        
        Args:
            name: Nombre del logger
            level: Nivel de log mínimo
            enable_console: Habilitar salida a consola
            enable_file: Habilitar salida a archivo
            log_file: Ruta del archivo de log
            include_timestamp: Incluir timestamp en logs
            include_context: Incluir contexto en logs
        """
        self.name = name
        self.level = level
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.log_file = log_file or f"{name}.log"
        self.include_timestamp = include_timestamp
        self.include_context = include_context
        
        # Configurar logger de Python
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Eliminar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar handlers
        if enable_console:
            self._setup_console_handler()
        
        if enable_file:
            self._setup_file_handler()
        
        # Contexto global
        self._context: Dict[str, Any] = {}
        
        logging.info(f"StructuredLogger inicializado: {name}")
    
    def _setup_console_handler(self) -> None:
        """Configurar handler de consola"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, self.level.value))
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def _setup_file_handler(self) -> None:
        """Configurar handler de archivo"""
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(getattr(logging, self.level.value))
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def _format_log(
        self,
        level: LogLevel,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Formatear log como JSON
        
        Args:
            level: Nivel de log
            message: Mensaje de log
            extra: Datos adicionales
            
        Returns:
            Log formateado como JSON
        """
        log_data: Dict[str, Any] = {
            'level': level.value,
            'logger': self.name,
            'message': message,
        }
        
        if self.include_timestamp:
            log_data['timestamp'] = datetime.now().isoformat()
        
        # Agregar contexto global
        if self.include_context:
            context = _log_context.get()
            if context:
                log_data['context'] = context
        
        # Agregar contexto del logger
        if self._context:
            log_data['logger_context'] = self._context
        
        # Agregar datos extra
        if extra:
            log_data['data'] = extra
        
        return json.dumps(log_data, ensure_ascii=False)
    
    def _log(
        self,
        level: LogLevel,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emitir log
        
        Args:
            level: Nivel de log
            message: Mensaje de log
            extra: Datos adicionales
        """
        log_message = self._format_log(level, message, extra)
        log_level = getattr(logging, level.value)
        self.logger.log(log_level, log_message)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log nivel DEBUG"""
        self._log(LogLevel.DEBUG, message, extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log nivel INFO"""
        self._log(LogLevel.INFO, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log nivel WARNING"""
        self._log(LogLevel.WARNING, message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log nivel ERROR"""
        self._log(LogLevel.ERROR, message, extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log nivel CRITICAL"""
        self._log(LogLevel.CRITICAL, message, extra)
    
    def exception(
        self,
        message: str,
        exception: Exception,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log de excepción con stack trace
        
        Args:
            message: Mensaje de log
            exception: Excepción capturada
            extra: Datos adicionales
        """
        if extra is None:
            extra = {}
        
        extra['exception_type'] = type(exception).__name__
        extra['exception_message'] = str(exception)
        
        self._log(LogLevel.ERROR, message, extra)
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Establecer valor en contexto global
        
        Args:
            key: Clave del contexto
            value: Valor del contexto
        """
        context = _log_context.get()
        context[key] = value
        _log_context.set(context)
    
    def get_context(self, key: str) -> Optional[Any]:
        """
        Obtener valor del contexto global
        
        Args:
            key: Clave del contexto
            
        Returns:
            Valor del contexto o None
        """
        context = _log_context.get()
        return context.get(key)
    
    def clear_context(self) -> None:
        """Limpiar contexto global"""
        _log_context.set({})
    
    def set_logger_context(self, key: str, value: Any) -> None:
        """
        Establecer valor en contexto del logger
        
        Args:
            key: Clave del contexto
            value: Valor del contexto
        """
        self._context[key] = value
    
    def clear_logger_context(self) -> None:
        """Limpiar contexto del logger"""
        self._context.clear()


class LogContext:
    """
    Gestor de contexto de log
    Permite agregar contexto temporal a los logs
    """
    
    def __init__(self, context: Dict[str, Any]):
        """
        Inicializar contexto de log
        
        Args:
            context: Datos del contexto
        """
        self.context = context
        self.previous_context = _log_context.get().copy()
    
    def __enter__(self):
        """Entrar en contexto"""
        new_context = self.previous_context.copy()
        new_context.update(self.context)
        _log_context.set(new_context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salir de contexto"""
        _log_context.set(self.previous_context)
        return False


def get_logger(name: str, **kwargs) -> StructuredLogger:
    """
    Obtener o crear logger estructurado
    
    Args:
        name: Nombre del logger
        **kwargs: Argumentos adicionales para StructuredLogger
        
    Returns:
        Logger estructurado
    """
    return StructuredLogger(name, **kwargs)


def log_context(context: Dict[str, Any]) -> LogContext:
    """
    Crear contexto de log temporal
    
    Args:
        context: Datos del contexto
        
    Returns:
        Contexto de log
    """
    return LogContext(context)
