"""
Paquete de utilidades para (π)NAD
"""

from .logger import PINADLogger, get_logger
from .exceptions import (
    PINADException,
    OCRException,
    DocumentProcessingException,
    ValidationException,
    ClientException,
    GoogleIntegrationException,
    AuthenticationException,
    DashboardException,
    ConfigurationException,
    FileException,
    APIException,
    ValidatorException,
    ErrorHandler
)

from .utils_native import (
    UserRole,
    LogLevel,
    ExportFormat,
    User,
    Session,
    AuthSystem,
    ConfigManager,
    DatabaseManager,
    ExportManager,
    Logger as NativeLogger,
    UtilsManager,
    auth_system,
    config_manager,
    database_manager,
    export_manager,
    logger as native_logger,
    utils_manager
)

__all__ = [
    'PINADLogger',
    'get_logger',
    'PINADException',
    'OCRException',
    'DocumentProcessingException',
    'ValidationException',
    'ClientException',
    'GoogleIntegrationException',
    'AuthenticationException',
    'DashboardException',
    'ConfigurationException',
    'FileException',
    'APIException',
    'ValidatorException',
    'ErrorHandler',
    'UserRole',
    'LogLevel',
    'ExportFormat',
    'User',
    'Session',
    'AuthSystem',
    'ConfigManager',
    'DatabaseManager',
    'ExportManager',
    'NativeLogger',
    'UtilsManager',
    'auth_system',
    'config_manager',
    'database_manager',
    'export_manager',
    'native_logger',
    'utils_manager'
]
