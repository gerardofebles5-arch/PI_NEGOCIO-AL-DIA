"""
Multi-Tenancy Manager para (π)NAD V6.0
Gestión completa de multi-tenancy con aislamiento de datos
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class TenantIsolationLevel(Enum):
    """Niveles de aislamiento de tenant"""
    SHARED_DATABASE = "shared_database"  # Base de datos compartida con tenant_id
    SCHEMA_ISOLATION = "schema_isolation"  # Schema separado por tenant
    DATABASE_ISOLATION = "database_isolation"  # Base de datos separada por tenant


class TenantStatus(Enum):
    """Estado del tenant"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    TRIAL = "trial"


class Tenant:
    """Modelo de Tenant"""
    
    def __init__(
        self,
        tenant_id: str,
        name: str,
        email: str,
        isolation_level: TenantIsolationLevel,
        status: TenantStatus = TenantStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.tenant_id = tenant_id
        self.name = name
        self.email = email
        self.isolation_level = isolation_level
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.metadata = metadata or {}
        
        logger.debug(f"Tenant inicializado: {tenant_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir tenant a diccionario"""
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'email': self.email,
            'isolation_level': self.isolation_level.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tenant':
        """Crear tenant desde diccionario"""
        return cls(
            tenant_id=data['tenant_id'],
            name=data['name'],
            email=data['email'],
            isolation_level=TenantIsolationLevel(data['isolation_level']),
            status=TenantStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {}),
        )


class TenantManager:
    """
    Gestor de multi-tenancy con aislamiento de datos
    Implementa patrones de aislamiento a nivel de aplicación y base de datos
    """
    
    def __init__(
        self,
        default_isolation_level: TenantIsolationLevel = TenantIsolationLevel.SHARED_DATABASE,
        enable_tenant_cache: bool = True,
        cache_ttl: int = 3600,  # 1 hora
    ):
        """
        Inicializar gestor de tenants
        
        Args:
            default_isolation_level: Nivel de aislamiento por defecto
            enable_tenant_cache: Habilitar caché de tenants
            cache_ttl: TTL de caché en segundos
        """
        self.default_isolation_level = default_isolation_level
        self.enable_tenant_cache = enable_tenant_cache
        self.cache_ttl = cache_ttl
        
        # Almacenamiento de tenants (en producción usar base de datos)
        self._tenants: Dict[str, Tenant] = {}
        self._tenant_cache: Dict[str, Dict[str, Any]] = {}
        self._current_tenant: Optional[str] = None
        
        logger.info("Tenant Manager inicializado")
    
    def generate_tenant_id(self, name: str, email: str) -> str:
        """
        Generar ID único de tenant basado en nombre y email
        
        Args:
            name: Nombre del tenant
            email: Email del tenant
            
        Returns:
            ID único de tenant
        """
        unique_string = f"{name.lower()}:{email.lower()}"
        hash_obj = hashlib.sha256(unique_string.encode())
        tenant_id = f"tenant_{hash_obj.hexdigest()[:16]}"
        
        logger.debug(f"Tenant ID generado: {tenant_id}")
        return tenant_id
    
    def create_tenant(
        self,
        name: str,
        email: str,
        isolation_level: Optional[TenantIsolationLevel] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tenant:
        """
        Crear nuevo tenant
        
        Args:
            name: Nombre del tenant
            email: Email del tenant
            isolation_level: Nivel de aislación (default: default)
            metadata: Metadata adicional
            
        Returns:
            Tenant creado
        """
        tenant_id = self.generate_tenant_id(name, email)
        
        if tenant_id in self._tenants:
            raise ValueError(f"Tenant con ID {tenant_id} ya existe")
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            email=email,
            isolation_level=isolation_level or self.default_isolation_level,
            metadata=metadata,
        )
        
        self._tenants[tenant_id] = tenant
        
        logger.info(f"Tenant creado: {tenant_id}")
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Obtener tenant por ID
        
        Args:
            tenant_id: ID del tenant
            
        Returns:
            Tenant o None si no existe
        """
        if self.enable_tenant_cache and tenant_id in self._tenant_cache:
            cached = self._tenant_cache[tenant_id]
            if datetime.now() - datetime.fromisoformat(cached['cached_at']) < timedelta(seconds=self.cache_ttl):
                return Tenant.from_dict(cached['tenant'])
        
        tenant = self._tenants.get(tenant_id)
        
        if tenant and self.enable_tenant_cache:
            self._tenant_cache[tenant_id] = {
                'tenant': tenant.to_dict(),
                'cached_at': datetime.now().isoformat(),
            }
        
        return tenant
    
    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[TenantStatus] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tenant:
        """
        Actualizar tenant
        
        Args:
            tenant_id: ID del tenant
            name: Nuevo nombre
            email: Nuevo email
            status: Nuevo estado
            metadata: Nueva metadata
            
        Returns:
            Tenant actualizado
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} no encontrado")
        
        if name:
            tenant.name = name
        if email:
            tenant.email = email
        if status:
            tenant.status = status
        if metadata:
            tenant.metadata.update(metadata)
        
        tenant.updated_at = datetime.now()
        
        # Invalidar caché
        if tenant_id in self._tenant_cache:
            del self._tenant_cache[tenant_id]
        
        logger.info(f"Tenant actualizado: {tenant_id}")
        return tenant
    
    def delete_tenant(self, tenant_id: str, soft_delete: bool = True) -> bool:
        """
        Eliminar tenant
        
        Args:
            tenant_id: ID del tenant
            soft_delete: Soft delete (marcar como eliminado) o hard delete
            
        Returns:
            True si eliminado exitosamente
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        if soft_delete:
            tenant.status = TenantStatus.DELETED
            tenant.updated_at = datetime.now()
            logger.info(f"Tenant soft-deleted: {tenant_id}")
        else:
            del self._tenants[tenant_id]
            if tenant_id in self._tenant_cache:
                del self._tenant_cache[tenant_id]
            logger.info(f"Tenant hard-deleted: {tenant_id}")
        
        return True
    
    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Tenant]:
        """
        Listar tenants con filtros
        
        Args:
            status: Filtrar por estado
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de tenants
        """
        tenants = list(self._tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        return tenants[offset:offset + limit]
    
    def set_current_tenant(self, tenant_id: str) -> bool:
        """
        Establecer tenant actual para el contexto de ejecución
        
        Args:
            tenant_id: ID del tenant
            
        Returns:
            True si establecido exitosamente
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        if tenant.status != TenantStatus.ACTIVE:
            raise ValueError(f"Tenant {tenant_id} no está activo")
        
        self._current_tenant = tenant_id
        logger.info(f"Tenant actual establecido: {tenant_id}")
        return True
    
    def get_current_tenant(self) -> Optional[Tenant]:
        """
        Obtener tenant actual
        
        Returns:
            Tenant actual o None
        """
        if self._current_tenant:
            return self.get_tenant(self._current_tenant)
        return None
    
    def clear_current_tenant(self) -> None:
        """Limpiar tenant actual"""
        self._current_tenant = None
        logger.debug("Tenant actual limpiado")
    
    def add_tenant_metadata(self, tenant_id: str, key: str, value: Any) -> bool:
        """
        Agregar metadata a tenant
        
        Args:
            tenant_id: ID del tenant
            key: Clave de metadata
            value: Valor de metadata
            
        Returns:
            True si agregado exitosamente
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        tenant.metadata[key] = value
        tenant.updated_at = datetime.now()
        
        # Invalidar caché
        if tenant_id in self._tenant_cache:
            del self._tenant_cache[tenant_id]
        
        return True
    
    def get_tenant_metadata(self, tenant_id: str) -> Dict[str, Any]:
        """
        Obtener metadata de tenant
        
        Args:
            tenant_id: ID del tenant
            
        Returns:
            Metadata del tenant
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return {}
        
        return tenant.metadata.copy()
    
    def get_tenant_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de tenants
        
        Returns:
            Estadísticas de tenants
        """
        tenants = list(self._tenants.values())
        
        return {
            'total_tenants': len(tenants),
            'active_tenants': len([t for t in tenants if t.status == TenantStatus.ACTIVE]),
            'suspended_tenants': len([t for t in tenants if t.status == TenantStatus.SUSPENDED]),
            'deleted_tenants': len([t for t in tenants if t.status == TenantStatus.DELETED]),
            'trial_tenants': len([t for t in tenants if t.status == TenantStatus.TRIAL]),
            'isolation_levels': {
                'shared_database': len([t for t in tenants if t.isolation_level == TenantIsolationLevel.SHARED_DATABASE]),
                'schema_isolation': len([t for t in tenants if t.isolation_level == TenantIsolationLevel.SCHEMA_ISOLATION]),
                'database_isolation': len([t for t in tenants if t.isolation_level == TenantIsolationLevel.DATABASE_ISOLATION]),
            },
        }


class TenantContext:
    """
    Contexto de tenant para aislamiento a nivel de aplicación
    Implementa Thread-Local Storage para aislamiento por hilo
    """
    
    def __init__(self):
        """Inicializar contexto de tenant"""
        self._tenant_id: Optional[str] = None
        self._metadata: Dict[str, Any] = {}
        
        logger.debug("Tenant Context inicializado")
    
    def set_tenant(self, tenant_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Establecer tenant en contexto
        
        Args:
            tenant_id: ID del tenant
            metadata: Metadata adicional
        """
        self._tenant_id = tenant_id
        self._metadata = metadata or {}
        logger.debug(f"Tenant establecido en contexto: {tenant_id}")
    
    def get_tenant(self) -> Optional[str]:
        """
        Obtener tenant del contexto
        
        Returns:
            ID del tenant o None
        """
        return self._tenant_id
    
    def clear_tenant(self) -> None:
        """Limpiar tenant del contexto"""
        self._tenant_id = None
        self._metadata = {}
        logger.debug("Tenant limpiado del contexto")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Obtener metadata del contexto
        
        Returns:
            Metadata del contexto
        """
        return self._metadata.copy()
    
    def is_tenant_set(self) -> bool:
        """
        Verificar si hay tenant establecido
        
        Returns:
            True si hay tenant establecido
        """
        return self._tenant_id is not None


# Contexto global de tenant (en producción usar Thread-Local Storage)
_tenant_context = TenantContext()


def get_tenant_context() -> TenantContext:
    """Obtener contexto global de tenant"""
    return _tenant_context


def set_tenant_context(tenant_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Establecer tenant en contexto global"""
    _tenant_context.set_tenant(tenant_id, metadata)


def get_current_tenant_id() -> Optional[str]:
    """Obtener ID del tenant actual del contexto"""
    return _tenant_context.get_tenant()


def clear_tenant_context() -> None:
    """Limpiar contexto de tenant"""
    _tenant_context.clear_tenant()
