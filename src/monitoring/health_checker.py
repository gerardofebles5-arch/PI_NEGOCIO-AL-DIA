"""
Health Checker para (π)NAD V6.0
Verificación de salud del sistema y componentes
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Estado de salud"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Resultado de verificación de salud"""
    component: str
    status: HealthStatus
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir resultado a diccionario"""
        return {
            'component': self.component,
            'status': self.status.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
        }


class HealthChecker:
    """
    Verificador de salud del sistema
    Implementa verificaciones de salud para componentes
    """
    
    def __init__(self):
        """Inicializar verificador de salud"""
        self._checks: Dict[str, Callable] = {}
        self._last_results: Dict[str, HealthCheckResult] = {}
        
        logger.info("HealthChecker inicializado")
    
    def register_check(
        self,
        name: str,
        check_func: Callable[[], HealthCheckResult],
    ) -> None:
        """
        Registrar verificación de salud
        
        Args:
            name: Nombre del componente
            check_func: Función de verificación
        """
        self._checks[name] = check_func
        logger.debug(f"Verificación registrada: {name}")
    
    def check_component(self, name: str) -> HealthCheckResult:
        """
        Verificar salud de componente específico
        
        Args:
            name: Nombre del componente
            
        Returns:
            Resultado de verificación
        """
        if name not in self._checks:
            return HealthCheckResult(
                component=name,
                status=HealthStatus.UNKNOWN,
                message="Verificación no registrada",
            )
        
        try:
            result = self._checks[name]()
            self._last_results[name] = result
            return result
        except Exception as e:
            logger.error(f"Error verificando {name}: {e}")
            result = HealthCheckResult(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error en verificación: {str(e)}",
            )
            self._last_results[name] = result
            return result
    
    def check_all(self) -> Dict[str, HealthCheckResult]:
        """
        Verificar salud de todos los componentes
        
        Returns:
            Diccionario con resultados por componente
        """
        results = {}
        for name in self._checks:
            results[name] = self.check_component(name)
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """
        Obtener estado general del sistema
        
        Returns:
            Estado general
        """
        if not self._last_results:
            return HealthStatus.UNKNOWN
        
        statuses = [r.status for r in self._last_results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        Obtener reporte completo de salud
        
        Returns:
            Reporte de salud
        """
        results = self.check_all()
        
        return {
            'overall_status': self.get_overall_status().value,
            'timestamp': datetime.now().isoformat(),
            'components': {
                name: result.to_dict()
                for name, result in results.items()
            },
        }


# Verificaciones predefinidas

def check_database_connection(
    connection_func: Callable[[], bool],
) -> Callable[[], HealthCheckResult]:
    """
    Crear verificación de conexión a base de datos
    
    Args:
        connection_func: Función que verifica conexión
        
    Returns:
        Función de verificación
    """
    def check() -> HealthCheckResult:
        try:
            is_connected = connection_func()
            if is_connected:
                return HealthCheckResult(
                    component="database",
                    status=HealthStatus.HEALTHY,
                    message="Conexión a base de datos exitosa",
                )
            else:
                return HealthCheckResult(
                    component="database",
                    status=HealthStatus.UNHEALTHY,
                    message="No se pudo conectar a base de datos",
                )
        except Exception as e:
            return HealthCheckResult(
                component="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Error verificando conexión: {str(e)}",
            )
    
    return check


def check_api_endpoint(
    url: str,
    timeout: int = 5,
) -> Callable[[], HealthCheckResult]:
    """
    Crear verificación de endpoint API
    
    Args:
        url: URL del endpoint
        timeout: Timeout en segundos
        
    Returns:
        Función de verificación
    """
    def check() -> HealthCheckResult:
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                return HealthCheckResult(
                    component="api",
                    status=HealthStatus.HEALTHY,
                    message=f"API respondió exitosamente (status: {response.status_code})",
                    details={'status_code': response.status_code},
                )
            else:
                return HealthCheckResult(
                    component="api",
                    status=HealthStatus.DEGRADED,
                    message=f"API respondió con error (status: {response.status_code})",
                    details={'status_code': response.status_code},
                )
        except requests.Timeout:
            return HealthCheckResult(
                component="api",
                status=HealthStatus.UNHEALTHY,
                message="Timeout al conectar a API",
            )
        except Exception as e:
            return HealthCheckResult(
                component="api",
                status=HealthStatus.UNHEALTHY,
                message=f"Error verificando API: {str(e)}",
            )
    
    return check


def check_disk_space(
    path: str,
    threshold_gb: float = 10.0,
) -> Callable[[], HealthCheckResult]:
    """
    Crear verificación de espacio en disco
    
    Args:
        path: Ruta a verificar
        threshold_gb: Umbral mínimo en GB
        
    Returns:
        Función de verificación
    """
    def check() -> HealthCheckResult:
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            free_gb = free / (1024 ** 3)
            
            if free_gb >= threshold_gb:
                return HealthCheckResult(
                    component="disk",
                    status=HealthStatus.HEALTHY,
                    message=f"Espacio en disco suficiente: {free_gb:.2f} GB libre",
                    details={
                        'total_gb': total / (1024 ** 3),
                        'used_gb': used / (1024 ** 3),
                        'free_gb': free_gb,
                        'threshold_gb': threshold_gb,
                    },
                )
            else:
                return HealthCheckResult(
                    component="disk",
                    status=HealthStatus.DEGRADED,
                    message=f"Espacio en disco bajo: {free_gb:.2f} GB libre",
                    details={
                        'total_gb': total / (1024 ** 3),
                        'used_gb': used / (1024 ** 3),
                        'free_gb': free_gb,
                        'threshold_gb': threshold_gb,
                    },
                )
        except Exception as e:
            return HealthCheckResult(
                component="disk",
                status=HealthStatus.UNKNOWN,
                message=f"Error verificando espacio en disco: {str(e)}",
            )
    
    return check


def check_memory_usage(
    threshold_percent: float = 90.0,
) -> Callable[[], HealthCheckResult]:
    """
    Crear verificación de uso de memoria
    
    Args:
        threshold_percent: Umbral máximo en porcentaje
        
    Returns:
        Función de verificación
    """
    def check() -> HealthCheckResult:
        try:
            import psutil
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent < threshold_percent:
                return HealthCheckResult(
                    component="memory",
                    status=HealthStatus.HEALTHY,
                    message=f"Uso de memoria normal: {usage_percent:.1f}%",
                    details={
                        'usage_percent': usage_percent,
                        'total_gb': memory.total / (1024 ** 3),
                        'available_gb': memory.available / (1024 ** 3),
                        'threshold_percent': threshold_percent,
                    },
                )
            else:
                return HealthCheckResult(
                    component="memory",
                    status=HealthStatus.DEGRADED,
                    message=f"Uso de memoria alto: {usage_percent:.1f}%",
                    details={
                        'usage_percent': usage_percent,
                        'total_gb': memory.total / (1024 ** 3),
                        'available_gb': memory.available / (1024 ** 3),
                        'threshold_percent': threshold_percent,
                    },
                )
        except Exception as e:
            return HealthCheckResult(
                component="memory",
                status=HealthStatus.UNKNOWN,
                message=f"Error verificando memoria: {str(e)}",
            )
    
    return check
