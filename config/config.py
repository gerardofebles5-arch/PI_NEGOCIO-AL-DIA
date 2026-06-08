"""
Archivo de configuración para (π)NAD
"""

import os
from typing import Dict, Optional, List


class Config:
    """Configuración principal del sistema (π)NAD"""
    
    # Configuración de Google Cloud
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'pinad-production')
    GOOGLE_CLOUD_REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'config/service_account.json')
    SERVICE_ACCOUNT_EMAIL = os.getenv('SERVICE_ACCOUNT_EMAIL', None)
    
    # Configuración de Google Forms
    FORMS_CREDENTIALS_PATH = os.getenv('FORMS_CREDENTIALS_PATH', 'config/service_account.json')
    
    # Configuración de Google Sheets
    SHEETS_CREDENTIALS_PATH = os.getenv('SHEETS_CREDENTIALS_PATH', 'config/service_account.json')
    SHEETS_ID = os.getenv('SHEETS_ID', None)
    
    # Configuración de Google Drive
    DRIVE_CREDENTIALS_PATH = os.getenv('DRIVE_CREDENTIALS_PATH', 'config/service_account.json')
    DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID', None)
    
    # Configuración de Document AI
    DOCUMENT_AI_LOCATION = os.getenv('DOCUMENT_AI_LOCATION', 'us')
    DOCUMENT_AI_PROCESSOR_ID = os.getenv('DOCUMENT_AI_PROCESSOR_ID', None)
    
    # Configuración de OAuth
    OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', None)
    OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', None)
    OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:5000/callback')
    
    # Configuración de Base de Datos
    CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME', None)
    DB_USER = os.getenv('DB_USER', 'pinad_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', None)
    DB_NAME = os.getenv('DB_NAME', 'pinad_db')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # Configuración de OCR
    OCR_LANGUAGES = ['es']
    OCR_USE_GPU = False
    OCR_CONFIDENCE_THRESHOLD = 0.7
    
    # Configuración de Validación
    VALIDATION_TIMEOUT_HOURS = 48
    HIGH_PRIORITY_THRESHOLD = 10
    MEDIUM_PRIORITY_THRESHOLD = 5
    
    # Configuración de Dashboard
    DASHBOARD_REFRESH_INTERVAL_MINUTES = 15
    
    # Configuración de API
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    API_VERSION = 'v1'
    API_KEY = os.getenv('API_KEY', None)
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Configuración de Firebase
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', None)
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', None)
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', None)
    FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL', None)
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', None)
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', None)
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', None)
    
    # Configuración de Multi-Tenancy
    DEFAULT_ISOLATION_LEVEL = os.getenv('DEFAULT_ISOLATION_LEVEL', 'shared_database')
    ENABLE_TENANT_CACHE = os.getenv('ENABLE_TENANT_CACHE', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))
    
    # Configuración de Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    
    # Configuración de Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/pinad.log')
    
    # Configuración de Archivos
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls', '.csv']
    
    # Configuración de Planes
    PLANS = {
        'basic': {
            'name': 'Básico',
            'price': 29,
            'transaction_limit': 100,
            'user_limit': 1,
            'validation_hours': 48
        },
        'professional': {
            'name': 'Profesional',
            'price': 79,
            'transaction_limit': 500,
            'user_limit': 3,
            'validation_hours': 24
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 199,
            'transaction_limit': float('inf'),
            'user_limit': float('inf'),
            'validation_hours': 4
        }
    }
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """
        Validar configuración
        
        Returns:
            Diccionario con estado de cada configuración
        """
        validation = {}
        
        # Validar configuraciones requeridas
        validation['oauth_configured'] = bool(cls.OAUTH_CLIENT_ID and cls.OAUTH_CLIENT_SECRET)
        validation['sheets_configured'] = bool(cls.SHEETS_ID or os.path.exists(cls.SHEETS_CREDENTIALS_PATH))
        validation['drive_configured'] = bool(cls.DRIVE_FOLDER_ID or os.path.exists(cls.DRIVE_CREDENTIALS_PATH))
        validation['document_ai_configured'] = bool(cls.DOCUMENT_AI_PROCESSOR_ID)
        validation['database_configured'] = bool(cls.DB_PASSWORD)
        
        return validation
    
    @classmethod
    def get_missing_configs(cls) -> List[str]:
        """
        Obtener configuraciones faltantes
        
        Returns:
            Lista de configuraciones faltantes
        """
        missing = []
        
        if not cls.OAUTH_CLIENT_ID:
            missing.append('OAUTH_CLIENT_ID')
        if not cls.OAUTH_CLIENT_SECRET:
            missing.append('OAUTH_CLIENT_SECRET')
        if not cls.SHEETS_ID and not os.path.exists(cls.SHEETS_CREDENTIALS_PATH):
            missing.append('SHEETS_ID or SHEETS_CREDENTIALS_PATH')
        if not cls.DRIVE_FOLDER_ID and not os.path.exists(cls.DRIVE_CREDENTIALS_PATH):
            missing.append('DRIVE_FOLDER_ID or DRIVE_CREDENTIALS_PATH')
        if not cls.DOCUMENT_AI_PROCESSOR_ID:
            missing.append('DOCUMENT_AI_PROCESSOR_ID')
        if not cls.DB_PASSWORD:
            missing.append('DB_PASSWORD')
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your-secret-key-change-in-production':
            missing.append('SECRET_KEY')
        if not cls.FIREBASE_PROJECT_ID:
            missing.append('FIREBASE_PROJECT_ID')
        
        return missing


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """Configuración de pruebas"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'
