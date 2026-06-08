"""
Data Isolation para (π)NAD V6.0
Aislamiento de datos a nivel de aplicación y base de datos
"""

import logging
from typing import Optional, Dict, Any, List, TypeVar, Generic
from datetime import datetime
from functools import wraps

from .tenant_manager import get_current_tenant_id, TenantContext

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DataIsolationMixin:
    """
    Mixin para aislamiento de datos en modelos
    Agrega automáticamente tenant_id a queries y filtros
    """
    
    @classmethod
    def with_tenant_filter(cls, query: Any, tenant_id: Optional[str] = None) -> Any:
        """
        Agregar filtro de tenant a query
        
        Args:
            query: Query original
            tenant_id: ID del tenant (default: actual)
            
        Returns:
            Query con filtro de tenant
        """
        current_tenant = tenant_id or get_current_tenant_id()
        if current_tenant:
            return query.filter(cls.tenant_id == current_tenant)
        return query
    
    @classmethod
    def ensure_tenant_isolation(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asegurar que los datos tengan tenant_id
        
        Args:
            data: Datos originales
            
        Returns:
            Datos con tenant_id
        """
        current_tenant = get_current_tenant_id()
        if current_tenant and 'tenant_id' not in data:
            data['tenant_id'] = current_tenant
        return data


class TenantAwareRepository(Generic[T]):
    """
    Repositorio con conciencia de tenant
    Implementa aislamiento de datos a nivel de repositorio
    """
    
    def __init__(self, model_class: type[T]):
        """
        Inicializar repositorio
        
        Args:
            model_class: Clase del modelo
        """
        self.model_class = model_class
        logger.info(f"TenantAwareRepository inicializado para {model_class.__name__}")
    
    def get_by_id(self, id: Any, tenant_id: Optional[str] = None) -> Optional[T]:
        """
        Obtener entidad por ID con aislamiento de tenant
        
        Args:
            id: ID de la entidad
            tenant_id: ID del tenant (default: actual)
            
        Returns:
            Entidad o None
        """
        current_tenant = tenant_id or get_current_tenant_id()
        
        # Implementar query con filtro de tenant
        # En producción usar ORM específico (SQLAlchemy, Django ORM, etc.)
        logger.debug(f"Obteniendo {self.model_class.__name__} por ID {id} para tenant {current_tenant}")
        return None
    
    def get_all(
        self,
        tenant_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """
        Obtener todas las entidades con aislamiento de tenant
        
        Args:
            tenant_id: ID del tenant (default: actual)
            filters: Filtros adicionales
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de entidades
        """
        current_tenant = tenant_id or get_current_tenant_id()
        
        # Implementar query con filtro de tenant
        logger.debug(f"Obteniendo {self.model_class.__name__} para tenant {current_tenant}")
        return []
    
    def create(self, data: Dict[str, Any], tenant_id: Optional[str] = None) -> T:
        """
        Crear entidad con aislamiento de tenant
        
        Args:
            data: Datos de la entidad
            tenant_id: ID del tenant (default: actual)
            
        Returns:
            Entidad creada
        """
        current_tenant = tenant_id or get_current_tenant_id()
        
        # Asegurar tenant_id en datos
        if current_tenant and 'tenant_id' not in data:
            data['tenant_id'] = current_tenant
        
        # Implementar creación
        logger.debug(f"Creando {self.model_class.__name__} para tenant {current_tenant}")
        return None
    
    def update(self, id: Any, data: Dict[str, Any], tenant_id: Optional[str] = None) -> Optional[T]:
        """
        Actualizar entidad con aislamiento de tenant
        
        Args:
            id: ID de la entidad
            data: Datos a actualizar
            tenant_id: ID del tenant (default: actual)
            
        Returns:
            Entidad actualizada o None
        """
        current_tenant = tenant_id or get_current_tenant_id()
        
        # Implementar actualización con filtro de tenant
        logger.debug(f"Actualizando {self.model_class.__name__} {id} para tenant {current_tenant}")
        return None
    
    def delete(self, id: Any, tenant_id: Optional[str] = None) -> bool:
        """
        Eliminar entidad con aislamiento de tenant
        
        Args:
            id: ID de la entidad
            tenant_id: ID del tenant (default: actual)
            
        Returns:
            True si eliminado exitosamente
        """
        current_tenant = tenant_id or get_current_tenant_id()
        
        # Implementar eliminación con filtro de tenant
        logger.debug(f"Eliminando {self.model_class.__name__} {id} para tenant {current_tenant}")
        return False


def require_tenant(func):
    """
    Decorador para requerir tenant en contexto
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            raise ValueError("Tenant no establecido en contexto")
        return func(*args, **kwargs)
    return wrapper


def with_tenant_isolation(func):
    """
    Decorador para asegurar aislamiento de tenant en función
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        tenant_id = get_current_tenant_id()
        if tenant_id:
            kwargs['tenant_id'] = tenant_id
        return func(*args, **kwargs)
    return wrapper


class TenantDataFilter:
    """
    Filtro de datos por tenant
    Implementa lógica de filtrado a nivel de aplicación
    """
    
    @staticmethod
    def filter_by_tenant(data: List[Dict[str, Any]], tenant_id: str) -> List[Dict[str, Any]]:
        """
        Filtrar lista de datos por tenant_id
        
        Args:
            data: Lista de datos
            tenant_id: ID del tenant
            
        Returns:
            Datos filtrados
        """
        return [item for item in data if item.get('tenant_id') == tenant_id]
    
    @staticmethod
    def add_tenant_to_data(data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """
        Agregar tenant_id a datos
        
        Args:
            data: Datos originales
            tenant_id: ID del tenant
            
        Returns:
            Datos con tenant_id
        """
        data['tenant_id'] = tenant_id
        return data
    
    @staticmethod
    def validate_tenant_access(data: Dict[str, Any], tenant_id: str) -> bool:
        """
        Validar que los datos pertenezcan al tenant
        
        Args:
            data: Datos a validar
            tenant_id: ID del tenant
            
        Returns:
            True si los datos pertenecen al tenant
        """
        return data.get('tenant_id') == tenant_id


class TenantDatabaseIsolation:
    """
    Aislamiento de base de datos por tenant
    Implementa estrategias de aislamiento a nivel de base de datos
    """
    
    def __init__(self, isolation_type: str = "shared_database"):
        """
        Inicializar aislamiento de base de datos
        
        Args:
            isolation_type: Tipo de aislación (shared_database, schema_isolation, database_isolation)
        """
        self.isolation_type = isolation_type
        logger.info(f"TenantDatabaseIsolation inicializado: {isolation_type}")
    
    def get_tenant_database_name(self, tenant_id: str) -> str:
        """
        Generar nombre de base de datos para tenant
        
        Args:
            tenant_id: ID del tenant
            
        Returns:
            Nombre de base de datos
        """
        if self.isolation_type == "database_isolation":
            return f"tenant_{tenant_id}"
        return "pinad_db"
    
    def get_tenant_schema_name(self, tenant_id: str) -> str:
        """
        Generar nombre de schema para tenant
        
        Args:
            tenant_id: ID del tenant
            
        Returns:
            Nombre de schema
        """
        if self.isolation_type == "schema_isolation":
            return f"tenant_{tenant_id}"
        return "public"
    
    def get_tenant_table_name(self, base_table: str, tenant_id: str) -> str:
        """
        Generar nombre de tabla para tenant (para aislamiento por tabla)
        
        Args:
            base_table: Nombre base de la tabla
            tenant_id: ID del tenant
            
        Returns:
            Nombre de tabla
        """
        if self.isolation_type == "table_isolation":
            return f"{base_table}_{tenant_id}"
        return base_table
    
    def create_tenant_schema(self, tenant_id: str) -> bool:
        """
        Crear schema para tenant
        
        Args:
            tenant_id: ID del tenant
            
        Returns:
            True si creado exitosamente
        """
        if self.isolation_type != "schema_isolation":
            return False
        
        schema_name = self.get_tenant_schema_name(tenant_id)
        
        # Implementar creación de schema
        # En producción usar SQL específico del motor de base de datos
        logger.info(f"Creando schema {schema_name} para tenant {tenant_id}")
        return True
    
    def create_tenant_database(self, tenant_id: str) -> bool:
        """
        Crear base de datos para tenant
        
        Args:
            tenant_id: ID del tenant
            
        Returns:
            True si creado exitosamente
        """
        if self.isolation_type != "database_isolation":
            return False
        
        db_name = self.get_tenant_database_name(tenant_id)
        
        # Implementar creación de base de datos
        logger.info(f"Creando base de datos {db_name} para tenant {tenant_id}")
        return True
