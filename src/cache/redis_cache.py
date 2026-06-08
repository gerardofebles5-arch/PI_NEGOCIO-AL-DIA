"""
Sistema de caché con Redis para (π)NAD
"""

import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
from src.utils.logger import get_logger


class RedisCache:
    """Sistema de caché con Redis para (π)NAD"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: str = None, 
                 decode_responses: bool = False):
        """
        Inicializar caché Redis
        
        Args:
            host: Host de Redis
            port: Puerto de Redis
            db: Número de base de datos Redis
            password: Contraseña de Redis
            decode_responses: Decodificar respuestas automáticamente
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        
        self.logger = get_logger('redis_cache')
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar cliente Redis"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Verificar conexión
            self.client.ping()
            self.logger.info("Redis cache inicializado exitosamente")
        except Exception as e:
            self.logger.error(f"Error inicializando Redis: {e}")
            self.client = None
    
    def set(self, key: str, value: Any, ttl: int = None, 
            serialize: bool = True) -> bool:
        """
        Guardar valor en caché
        
        Args:
            key: Clave de caché
            value: Valor a guardar
            ttl: Tiempo de vida en segundos
            serialize: Serializar valor (pickle/json)
            
        Returns:
            True si exitoso, False si falló
        """
        if not self.client:
            return False
        
        try:
            if serialize:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                else:
                    value = pickle.dumps(value)
            
            if ttl:
                return self.client.setex(key, ttl, value)
            else:
                return self.client.set(key, value)
        except Exception as e:
            self.logger.error(f"Error guardando en caché: {e}")
            return False
    
    def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """
        Obtener valor de caché
        
        Args:
            key: Clave de caché
            deserialize: Deserializar valor
            
        Returns:
            Valor almacenado o None si no existe
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            
            if value is None:
                return None
            
            if deserialize:
                try:
                    # Intentar deserializar como JSON primero
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Si falla, intentar con pickle
                    try:
                        return pickle.loads(value)
                    except:
                        return value.decode('utf-8') if isinstance(value, bytes) else value
            
            return value
        except Exception as e:
            self.logger.error(f"Error obteniendo de caché: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Eliminar valor de caché
        
        Args:
            key: Clave de caché
            
        Returns:
            True si exitoso, False si falló
        """
        if not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            self.logger.error(f"Error eliminando de caché: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Verificar si clave existe en caché
        
        Args:
            key: Clave de caché
            
        Returns:
            True si existe, False si no
        """
        if not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            self.logger.error(f"Error verificando existencia en caché: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Establecer tiempo de vida de clave
        
        Args:
            key: Clave de caché
            ttl: Tiempo de vida en segundos
            
        Returns:
            True si exitoso, False si falló
        """
        if not self.client:
            return False
        
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            self.logger.error(f"Error estableciendo TTL: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        Obtener tiempo de vida restante de clave
        
        Args:
            key: Clave de caché
            
        Returns:
            TTL en segundos, -1 si no tiene TTL, -2 si no existe
        """
        if not self.client:
            return -2
        
        try:
            return self.client.ttl(key)
        except Exception as e:
            self.logger.error(f"Error obteniendo TTL: {e}")
            return -2
    
    def clear(self) -> bool:
        """
        Limpiar toda la caché
        
        Returns:
            True si exitoso, False si falló
        """
        if not self.client:
            return False
        
        try:
            return bool(self.client.flushdb())
        except Exception as e:
            self.logger.error(f"Error limpiando caché: {e}")
            return False
    
    def get_many(self, keys: list) -> dict:
        """
        Obtener múltiples valores de caché
        
        Args:
            keys: Lista de claves
            
        Returns:
            Diccionario con clave-valor
        """
        if not self.client:
            return {}
        
        try:
            values = self.client.mget(keys)
            return dict(zip(keys, values))
        except Exception as e:
            self.logger.error(f"Error obteniendo múltiples valores: {e}")
            return {}
    
    def set_many(self, mapping: dict, ttl: int = None) -> bool:
        """
        Guardar múltiples valores en caché
        
        Args:
            mapping: Diccionario clave-valor
            ttl: Tiempo de vida en segundos
            
        Returns:
            True si exitoso, False si falló
        """
        if not self.client:
            return False
        
        try:
            if ttl:
                # Para TTL, necesitamos usar setex para cada clave
                for key, value in mapping.items():
                    self.set(key, value, ttl)
            else:
                self.client.mset(mapping)
            return True
        except Exception as e:
            self.logger.error(f"Error guardando múltiples valores: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Incrementar valor numérico en caché
        
        Args:
            key: Clave de caché
            amount: Cantidad a incrementar
            
        Returns:
            Nuevo valor o None si falló
        """
        if not self.client:
            return None
        
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            self.logger.error(f"Error incrementando valor: {e}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrementar valor numérico en caché
        
        Args:
            key: Clave de caché
            amount: Cantidad a decrementar
            
        Returns:
            Nuevo valor o None si falló
        """
        if not self.client:
            return None
        
        try:
            return self.client.decrby(key, amount)
        except Exception as e:
            self.logger.error(f"Error decrementando valor: {e}")
            return None
    
    def get_stats(self) -> dict:
        """
        Obtener estadísticas de Redis
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.client:
            return {}
        
        try:
            info = self.client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'total_commands': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}


class CacheManager:
    """Gestor de caché para (π)NAD"""
    
    def __init__(self, cache: RedisCache = None):
        """
        Inicializar gestor de caché
        
        Args:
            cache: Instancia de RedisCache
        """
        self.cache = cache or RedisCache()
        self.logger = get_logger('cache_manager')
    
    def cache_client_data(self, client_id: str, data: dict, ttl: int = 3600):
        """
        Cachear datos de cliente
        
        Args:
            client_id: ID del cliente
            data: Datos del cliente
            ttl: Tiempo de vida en segundos (default: 1 hora)
        """
        key = f"client:{client_id}"
        self.cache.set(key, data, ttl)
        self.logger.info(f"Cliente {client_id} cacheado por {ttl}s")
    
    def get_client_data(self, client_id: str) -> Optional[dict]:
        """
        Obtener datos de cliente de caché
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Datos del cliente o None
        """
        key = f"client:{client_id}"
        return self.cache.get(key)
    
    def cache_dashboard_data(self, client_id: str, dashboard_data: dict, ttl: int = 900):
        """
        Cachear datos de dashboard
        
        Args:
            client_id: ID del cliente
            dashboard_data: Datos del dashboard
            ttl: Tiempo de vida en segundos (default: 15 minutos)
        """
        key = f"dashboard:{client_id}"
        self.cache.set(key, dashboard_data, ttl)
        self.logger.info(f"Dashboard de cliente {client_id} cacheado por {ttl}s")
    
    def get_dashboard_data(self, client_id: str) -> Optional[dict]:
        """
        Obtener datos de dashboard de caché
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Datos del dashboard o None
        """
        key = f"dashboard:{client_id}"
        return self.cache.get(key)
    
    def cache_document_result(self, document_id: str, result: dict, ttl: int = 7200):
        """
        Cachear resultado de procesamiento de documento
        
        Args:
            document_id: ID del documento
            result: Resultado del procesamiento
            ttl: Tiempo de vida en segundos (default: 2 horas)
        """
        key = f"document:{document_id}"
        self.cache.set(key, result, ttl)
        self.logger.info(f"Documento {document_id} cacheado por {ttl}s")
    
    def get_document_result(self, document_id: str) -> Optional[dict]:
        """
        Obtener resultado de documento de caché
        
        Args:
            document_id: ID del documento
            
        Returns:
            Resultado del procesamiento o None
        """
        key = f"document:{document_id}"
        return self.cache.get(key)
    
    def cache_api_response(self, endpoint: str, params: dict, response: dict, ttl: int = 300):
        """
        Cachear respuesta de API
        
        Args:
            endpoint: Endpoint de API
            params: Parámetros de la petición
            response: Respuesta de la API
            ttl: Tiempo de vida en segundos (default: 5 minutos)
        """
        import hashlib
        key = f"api:{endpoint}:{hashlib.md5(str(params).encode()).hexdigest()}"
        self.cache.set(key, response, ttl)
        self.logger.info(f"API response cacheada para {endpoint}")
    
    def get_api_response(self, endpoint: str, params: dict) -> Optional[dict]:
        """
        Obtener respuesta de API de caché
        
        Args:
            endpoint: Endpoint de API
            params: Parámetros de la petición
            
        Returns:
            Respuesta cacheada o None
        """
        import hashlib
        key = f"api:{endpoint}:{hashlib.md5(str(params).encode()).hexdigest()}"
        return self.cache.get(key)
    
    def invalidate_client_cache(self, client_id: str):
        """
        Invalidar caché de cliente
        
        Args:
            client_id: ID del cliente
        """
        keys = [
            f"client:{client_id}",
            f"dashboard:{client_id}"
        ]
        
        for key in keys:
            self.cache.delete(key)
        
        self.logger.info(f"Caché de cliente {client_id} invalidada")
    
    def invalidate_document_cache(self, document_id: str):
        """
        Invalidar caché de documento
        
        Args:
            document_id: ID del documento
        """
        key = f"document:{document_id}"
        self.cache.delete(key)
        self.logger.info(f"Caché de documento {document_id} invalidada")
    
    def get_cache_stats(self) -> dict:
        """
        Obtener estadísticas de caché
        
        Returns:
            Diccionario con estadísticas
        """
        return self.cache.get_stats()
