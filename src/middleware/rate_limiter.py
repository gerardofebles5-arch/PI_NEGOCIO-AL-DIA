"""
Sistema de rate limiting para (π)NAD
"""

from functools import wraps
from flask import request, jsonify, g
from typing import Dict, Optional
import time
from src.cache.redis_cache import RedisCache
from src.utils.logger import get_logger


class RateLimiter:
    """Limitador de tasa de peticiones para (π)NAD"""
    
    def __init__(self, cache: RedisCache = None):
        """
        Inicializar limitador de tasa
        
        Args:
            cache: Instancia de RedisCache
        """
        self.cache = cache or RedisCache()
        self.logger = get_logger('rate_limiter')
    
    def is_allowed(self, key: str, limit: int, window: int) -> Dict:
        """
        Verificar si petición está permitida
        
        Args:
            key: Clave única para identificar al usuario/IP
            limit: Límite de peticiones
            window: Ventana de tiempo en segundos
            
        Returns:
            Diccionario con resultado
        """
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # Obtener peticiones anteriores
            requests_key = f"rate_limit:{key}"
            requests = self.cache.get(requests_key)
            
            if not requests:
                requests = []
            
            # Filtrar peticiones fuera de ventana
            requests = [r for r in requests if r > window_start]
            
            # Verificar límite
            if len(requests) >= limit:
                return {
                    'allowed': False,
                    'limit': limit,
                    'remaining': 0,
                    'reset': window_start + window
                }
            
            # Agregar petición actual
            requests.append(current_time)
            self.cache.set(requests_key, requests, ttl=window)
            
            return {
                'allowed': True,
                'limit': limit,
                'remaining': limit - len(requests),
                'reset': window_start + window
            }
        except Exception as e:
            self.logger.error(f"Error verificando rate limit: {e}")
            # En caso de error, permitir la petición
            return {'allowed': True, 'limit': limit, 'remaining': limit, 'reset': 0}
    
    def cleanup_old_keys(self):
        """Limpiar claves antiguas (opcional, Redis maneja esto con TTL)"""
        pass


class RateLimitConfig:
    """Configuración de límites de tasa"""
    
    # Límites por defecto
    DEFAULT_LIMITS = {
        'default': {'limit': 100, 'window': 3600},  # 100 peticiones por hora
        'api': {'limit': 1000, 'window': 3600},  # 1000 peticiones por hora
        'upload': {'limit': 10, 'window': 60},  # 10 uploads por minuto
        'validation': {'limit': 50, 'window': 3600},  # 50 validaciones por hora
        'dashboard': {'limit': 30, 'window': 60},  # 30 dashboards por minuto
    }
    
    # Límites por tipo de usuario
    USER_LIMITS = {
        'client': {'limit': 200, 'window': 3600},
        'validator': {'limit': 500, 'window': 3600},
        'admin': {'limit': 1000, 'window': 3600}
    }


def rate_limit(limit: int = 100, window: int = 3600, key_func=None, 
               rate_limiter: RateLimiter = None):
    """
    Decorador para limitar tasa de peticiones
    
    Args:
        limit: Límite de peticiones
        window: Ventana de tiempo en segundos
        key_func: Función para generar clave única
        rate_limiter: Instancia de RateLimiter
        
    Returns:
        Decorador
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = rate_limiter or RateLimiter()
            
            # Generar clave única
            if key_func:
                key = key_func(request)
            else:
                # Usar IP por defecto
                key = request.remote_addr
            
            # Verificar límite
            result = limiter.is_allowed(key, limit, window)
            
            if not result['allowed']:
                # Agregar headers de rate limit
                g.rate_limit = {
                    'limit': limit,
                    'remaining': result['remaining'],
                    'reset': result['reset']
                }
                
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': limit,
                    'remaining': result['remaining'],
                    'reset': result['reset']
                }), 429
            
            # Agregar headers de rate limit
            g.rate_limit = {
                'limit': limit,
                'remaining': result['remaining'],
                'reset': result['reset']
            }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit_by_user(limit: int = 100, window: int = 3600, 
                      rate_limiter: RateLimiter = None):
    """
    Decorador para limitar tasa por usuario
    
    Args:
        limit: Límite de peticiones
        window: Ventana de tiempo en segundos
        rate_limiter: Instancia de RateLimiter
        
    Returns:
        Decorador
    """
    def user_key_func(request):
        """Generar clave basada en usuario"""
        if hasattr(request, 'current_user') and request.current_user:
            return f"user:{request.current_user.get('user_id')}"
        return request.remote_addr
    
    return rate_limit(limit, window, user_key_func, rate_limiter)


def rate_limit_by_ip(limit: int = 100, window: int = 3600,
                    rate_limiter: RateLimiter = None):
    """
    Decorador para limitar tasa por IP
    
    Args:
        limit: Límite de peticiones
        window: Ventana de tiempo en segundos
        rate_limiter: Instancia de RateLimiter
        
    Returns:
        Decorador
    """
    def ip_key_func(request):
        """Generar clave basada en IP"""
        return f"ip:{request.remote_addr}"
    
    return rate_limit(limit, window, ip_key_func, rate_limiter)


def rate_limit_by_endpoint(limit: int = 100, window: int = 3600,
                          rate_limiter: RateLimiter = None):
    """
    Decorador para limitar tasa por endpoint
    
    Args:
        limit: Límite de peticiones
        window: Ventana de tiempo en segundos
        rate_limiter: Instancia de RateLimiter
        
    Returns:
        Decorador
    """
    def endpoint_key_func(request):
        """Generar clave basada en endpoint"""
        return f"endpoint:{request.endpoint}:{request.remote_addr}"
    
    return rate_limit(limit, window, endpoint_key_func, rate_limiter)


class RateLimitMiddleware:
    """Middleware de rate limiting para Flask"""
    
    def __init__(self, app=None, rate_limiter: RateLimiter = None):
        """
        Inicializar middleware
        
        Args:
            app: Aplicación Flask
            rate_limiter: Instancia de RateLimiter
        """
        self.rate_limiter = rate_limiter or RateLimiter()
        self.logger = get_logger('rate_limit_middleware')
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Inicializar con aplicación Flask
        
        Args:
            app: Aplicación Flask
        """
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        self.logger.info("Rate limiting middleware inicializado")
    
    def _before_request(self):
        """Ejecutar antes de cada petición"""
        # Obtener configuración para el endpoint
        endpoint = request.endpoint
        config = RateLimitConfig.DEFAULT_LIMITS.get(endpoint, RateLimitConfig.DEFAULT_LIMITS['default'])
        
        # Verificar límite
        key = f"ip:{request.remote_addr}"
        result = self.rate_limiter.is_allowed(key, config['limit'], config['window'])
        
        if not result['allowed']:
            return jsonify({
                'error': 'Rate limit exceeded',
                'limit': config['limit'],
                'remaining': result['remaining'],
                'reset': result['reset']
            }), 429
    
    def _after_request(self, response):
        """Ejecutar después de cada petición"""
        # Agregar headers de rate limit
        if hasattr(g, 'rate_limit'):
            response.headers['X-RateLimit-Limit'] = str(g.rate_limit['limit'])
            response.headers['X-RateLimit-Remaining'] = str(g.rate_limit['remaining'])
            response.headers['X-RateLimit-Reset'] = str(g.rate_limit['reset'])
        
        return response


class AdvancedRateLimiter:
    """Limitador de tasa avanzado con algoritmos"""
    
    def __init__(self, cache: RedisCache = None):
        """
        Inicializar limitador avanzado
        
        Args:
            cache: Instancia de RedisCache
        """
        self.cache = cache or RedisCache()
        self.logger = get_logger('advanced_rate_limiter')
    
    def token_bucket(self, key: str, capacity: int, refill_rate: float) -> Dict:
        """
        Algoritmo de Token Bucket
        
        Args:
            key: Clave única
            capacity: Capacidad del bucket
            refill_rate: Tasa de relleno (tokens por segundo)
            
        Returns:
            Diccionario con resultado
        """
        try:
            current_time = time.time()
            
            # Obtener estado del bucket
            bucket_key = f"token_bucket:{key}"
            bucket_state = self.cache.get(bucket_key)
            
            if not bucket_state:
                bucket_state = {
                    'tokens': capacity,
                    'last_update': current_time
                }
            
            # Calcular tokens rellenados
            time_passed = current_time - bucket_state['last_update']
            tokens_to_add = time_passed * refill_rate
            bucket_state['tokens'] = min(capacity, bucket_state['tokens'] + tokens_to_add)
            bucket_state['last_update'] = current_time
            
            # Verificar si hay tokens disponibles
            if bucket_state['tokens'] >= 1:
                bucket_state['tokens'] -= 1
                self.cache.set(bucket_key, bucket_state, ttl=3600)
                
                return {
                    'allowed': True,
                    'remaining_tokens': bucket_state['tokens']
                }
            else:
                self.cache.set(bucket_key, bucket_state, ttl=3600)
                
                return {
                    'allowed': False,
                    'remaining_tokens': bucket_state['tokens'],
                    'retry_after': (1 - bucket_state['tokens']) / refill_rate
                }
        except Exception as e:
            self.logger.error(f"Error en token bucket: {e}")
            return {'allowed': True, 'remaining_tokens': capacity}
    
    def sliding_window(self, key: str, limit: int, window: int) -> Dict:
        """
        Algoritmo de Sliding Window
        
        Args:
            key: Clave única
            limit: Límite de peticiones
            window: Ventana de tiempo en segundos
            
        Returns:
            Diccionario con resultado
        """
        try:
            current_time = time.time()
            window_start = current_time - window
            
            # Obtener peticiones
            requests_key = f"sliding_window:{key}"
            requests = self.cache.get(requests_key)
            
            if not requests:
                requests = []
            
            # Filtrar peticiones fuera de ventana
            requests = [r for r in requests if r > window_start]
            
            # Verificar límite
            if len(requests) >= limit:
                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset': requests[0] + window
                }
            
            # Agregar petición
            requests.append(current_time)
            self.cache.set(requests_key, requests, ttl=window)
            
            return {
                'allowed': True,
                'remaining': limit - len(requests),
                'reset': window_start + window
            }
        except Exception as e:
            self.logger.error(f"Error en sliding window: {e}")
            return {'allowed': True, 'remaining': limit, 'reset': 0}
