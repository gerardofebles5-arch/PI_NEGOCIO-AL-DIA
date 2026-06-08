"""
Archivo de configuración local para (π)NAD
Versión que funciona sin Google Cloud (modo local)
"""

import os
from typing import Dict, Optional, List


class LocalConfig:
    """Configuración local del sistema (π)NAD - Sin Google Cloud"""
    
    # Configuración de Google Cloud (desactivada)
    GOOGLE_CLOUD_ENABLED = False
    GOOGLE_CLOUD_PROJECT = None
    GOOGLE_CLOUD_REGION = None
    GOOGLE_APPLICATION_CREDENTIALS = None
    SERVICE_ACCOUNT_EMAIL = None
    
    # Configuración de Google Forms (desactivada)
    FORMS_CREDENTIALS_PATH = None
    
    # Configuración de Google Sheets (desactivada)
    SHEETS_CREDENTIALS_PATH = None
    SHEETS_ID = None
    
    # Configuración de Google Drive (desactivada)
    DRIVE_CREDENTIALS_PATH = None
    DRIVE_FOLDER_ID = None
    
    # Configuración de Document AI (desactivada)
    DOCUMENT_AI_LOCATION = None
    DOCUMENT_AI_PROCESSOR_ID = None
    
    # Configuración de OAuth (opcional - para desarrollo local)
    OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', None)
    OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', None)
    OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:5000/callback')
    
    # Configuración de Base de Datos Local (SQLite)
    USE_LOCAL_DB = True
    DB_TYPE = 'sqlite'
    DB_PATH = os.getenv('DB_PATH', 'data/pinad_local.db')
    DB_HOST = None
    DB_PORT = None
    DB_USER = None
    DB_PASSWORD = None
    DB_NAME = None
    
    # Configuración de OCR (local)
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
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración de Firebase (desactivada)
    FIREBASE_ENABLED = False
    FIREBASE_PROJECT_ID = None
    FIREBASE_API_KEY = None
    FIREBASE_AUTH_DOMAIN = None
    FIREBASE_DATABASE_URL = None
    FIREBASE_STORAGE_BUCKET = None
    FIREBASE_MESSAGING_SENDER_ID = None
    FIREBASE_APP_ID = None
    
    # Configuración de Multi-Tenancy (local)
    DEFAULT_ISOLATION_LEVEL = 'shared_database'
    ENABLE_TENANT_CACHE = True
    CACHE_TTL = 3600
    
    # Configuración de Environment
    ENVIRONMENT = 'local'
    DEBUG = True
    
    # Configuración de Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/pinad_local.log')
    
    # Configuración de Archivos Local
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls', '.csv']
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'data/uploads')
    EXPORT_DIR = os.getenv('EXPORT_DIR', 'data/exports')
    BACKUP_DIR = os.getenv('BACKUP_DIR', 'data/backups')
    
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
        Validar configuración local
        
        Returns:
            Diccionario con estado de cada configuración
        """
        validation = {}
        
        # Validar configuraciones requeridas para modo local
        validation['local_db_configured'] = cls.USE_LOCAL_DB
        validation['local_storage_configured'] = os.path.exists(cls.UPLOAD_DIR)
        validation['api_configured'] = bool(cls.API_BASE_URL)
        validation['secret_key_configured'] = bool(cls.SECRET_KEY)
        
        return validation
    
    @classmethod
    def get_missing_configs(cls) -> List[str]:
        """
        Obtener configuraciones faltantes
        
        Returns:
            Lista de configuraciones faltantes
        """
        missing = []
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            missing.append('SECRET_KEY')
        
        if not os.path.exists(cls.UPLOAD_DIR):
            missing.append('UPLOAD_DIR')
        
        return missing


class LocalDevelopmentConfig(LocalConfig):
    """Configuración de desarrollo local"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class LocalProductionConfig(LocalConfig):
    """Configuración de producción local"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
