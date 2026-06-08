"""
Sistema de monitoreo con Prometheus para (π)NAD
"""

from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
from flask import Response
from typing import Dict, Optional
from src.utils.logger import get_logger


class PrometheusMetrics:
    """Métricas de Prometheus para (π)NAD"""
    
    def __init__(self, registry: CollectorRegistry = None):
        """
        Inicializar métricas de Prometheus
        
        Args:
            registry: Registry de Prometheus
        """
        self.registry = registry or CollectorRegistry()
        self.logger = get_logger('prometheus_metrics')
        
        # Contadores
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total de peticiones HTTP',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.document_processing_total = Counter(
            'document_processing_total',
            'Total de documentos procesados',
            ['document_type', 'status'],
            registry=self.registry
        )
        
        self.validation_total = Counter(
            'validation_total',
            'Total de validaciones',
            ['action', 'status'],
            registry=self.registry
        )
        
        self.webhook_total = Counter(
            'webhook_total',
            'Total de webhooks disparados',
            ['event', 'status'],
            registry=self.registry
        )
        
        # Histogramas
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'Duración de peticiones HTTP',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.document_processing_duration = Histogram(
            'document_processing_duration_seconds',
            'Duración de procesamiento de documentos',
            ['document_type'],
            registry=self.registry
        )
        
        self.validation_duration = Histogram(
            'validation_duration_seconds',
            'Duración de validaciones',
            registry=self.registry
        )
        
        self.ocr_confidence = Histogram(
            'ocr_confidence',
            'Confianza de OCR',
            ['document_type'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # Gauges
        self.active_connections = Gauge(
            'active_connections',
            'Conexiones activas',
            registry=self.registry
        )
        
        self.pending_validations = Gauge(
            'pending_validations',
            'Validaciones pendientes',
            registry=self.registry
        )
        
        self.documents_in_queue = Gauge(
            'documents_in_queue',
            'Documentos en cola de procesamiento',
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'cache_hit_rate',
            'Tasa de aciertos de caché',
            registry=self.registry
        )
        
        self.database_connections = Gauge(
            'database_connections',
            'Conexiones a base de datos',
            registry=self.registry
        )
        
        # Info
        self.app_info = Info(
            'pinad_info',
            'Información de la aplicación (π)NAD',
            registry=self.registry
        )
        
        self.app_info.info({
            'version': '1.0.0',
            'name': 'pinad',
            'description': 'Sistema de contabilidad automatizada'
        })
    
    def track_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """
        Rastrear petición HTTP
        
        Args:
            method: Método HTTP
            endpoint: Endpoint
            status: Código de estado
            duration: Duración en segundos
        """
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def track_document_processing(self, document_type: str, status: str, duration: float, confidence: float = None):
        """
        Rastrear procesamiento de documento
        
        Args:
            document_type: Tipo de documento
            status: Estado del procesamiento
            duration: Duración en segundos
            confidence: Confianza de OCR
        """
        self.document_processing_total.labels(document_type=document_type, status=status).inc()
        self.document_processing_duration.labels(document_type=document_type).observe(duration)
        
        if confidence is not None:
            self.ocr_confidence.labels(document_type=document_type).observe(confidence)
    
    def track_validation(self, action: str, status: str, duration: float):
        """
        Rastrear validación
        
        Args:
            action: Acción de validación
            status: Estado de validación
            duration: Duración en segundos
        """
        self.validation_total.labels(action=action, status=status).inc()
        self.validation_duration.observe(duration)
    
    def track_webhook(self, event: str, status: str):
        """
        Rastrear webhook
        
        Args:
            event: Tipo de evento
            status: Estado del webhook
        """
        self.webhook_total.labels(event=event, status=status).inc()
    
    def update_active_connections(self, count: int):
        """
        Actualizar conexiones activas
        
        Args:
            count: Número de conexiones
        """
        self.active_connections.set(count)
    
    def update_pending_validations(self, count: int):
        """
        Actualizar validaciones pendientes
        
        Args:
            count: Número de validaciones pendientes
        """
        self.pending_validations.set(count)
    
    def update_documents_in_queue(self, count: int):
        """
        Actualizar documentos en cola
        
        Args:
            count: Número de documentos en cola
        """
        self.documents_in_queue.set(count)
    
    def update_cache_hit_rate(self, rate: float):
        """
        Actualizar tasa de aciertos de caché
        
        Args:
            rate: Tasa de aciertos (0-1)
        """
        self.cache_hit_rate.set(rate)
    
    def update_database_connections(self, count: int):
        """
        Actualizar conexiones a base de datos
        
        Args:
            count: Número de conexiones
        """
        self.database_connections.set(count)
    
    def get_metrics(self) -> str:
        """
        Obtener métricas en formato Prometheus
        
        Returns:
            Métricas en formato Prometheus
        """
        return generate_latest(self.registry)


class MetricsMiddleware:
    """Middleware para recolectar métricas de Flask"""
    
    def __init__(self, app=None, metrics: PrometheusMetrics = None):
        """
        Inicializar middleware de métricas
        
        Args:
            app: Aplicación Flask
            metrics: Instancia de PrometheusMetrics
        """
        self.metrics = metrics or PrometheusMetrics()
        self.logger = get_logger('metrics_middleware')
        
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
        
        # Endpoint de métricas
        @app.route('/metrics')
        def metrics_endpoint():
            return Response(self.metrics.get_metrics(), mimetype='text/plain')
        
        self.logger.info("Middleware de métricas inicializado")
    
    def _before_request(self):
        """Ejecutar antes de cada petición"""
        import time
        g.start_time = time.time()
    
    def _after_request(self, response):
        """Ejecutar después de cada petición"""
        import time
        
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            self.metrics.track_http_request(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code,
                duration=duration
            )
        
        return response


class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self):
        """Inicializar verificador de salud"""
        self.logger = get_logger('health_checker')
        self.checks = {}
    
    def register_check(self, name: str, check_func):
        """
        Registrar verificación de salud
        
        Args:
            name: Nombre de la verificación
            check_func: Función de verificación
        """
        self.checks[name] = check_func
        self.logger.info(f"Verificación registrada: {name}")
    
    def check_all(self) -> Dict:
        """
        Ejecutar todas las verificaciones
        
        Returns:
            Diccionario con resultados
        """
        results = {
            'status': 'healthy',
            'checks': {},
            'timestamp': None
        }
        
        import datetime
        results['timestamp'] = datetime.datetime.now().isoformat()
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results['checks'][name] = {
                    'status': 'pass' if result else 'fail',
                    'result': result
                }
                
                if not result:
                    results['status'] = 'unhealthy'
            except Exception as e:
                results['checks'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
                results['status'] = 'unhealthy'
        
        return results
    
    def check_database(self) -> bool:
        """Verificar conexión a base de datos"""
        try:
            from src.database.database import DatabaseManager
            db = DatabaseManager()
            with db.get_session() as session:
                session.execute('SELECT 1')
            return True
        except Exception as e:
            self.logger.error(f"Error verificando base de datos: {e}")
            return False
    
    def check_redis(self) -> bool:
        """Verificar conexión a Redis"""
        try:
            from src.cache.redis_cache import RedisCache
            cache = RedisCache()
            cache.client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Error verificando Redis: {e}")
            return False
    
    def check_google_integrations(self) -> bool:
        """Verificar integraciones de Google"""
        try:
            from src.integrations.google_sheets import GoogleSheetsIntegration
            sheets = GoogleSheetsIntegration()
            return sheets.sheets_service is not None
        except Exception as e:
            self.logger.error(f"Error verificando integraciones: {e}")
            return False
    
    def check_storage(self) -> bool:
        """Verificar almacenamiento"""
        try:
            from src.storage.cloud_storage import CloudStorageManager
            storage = CloudStorageManager()
            return storage.bucket is not None
        except Exception as e:
            self.logger.error(f"Error verificando almacenamiento: {e}")
            return False


class PerformanceMonitor:
    """Monitor de rendimiento"""
    
    def __init__(self, metrics: PrometheusMetrics = None):
        """
        Inicializar monitor de rendimiento
        
        Args:
            metrics: Instancia de PrometheusMetrics
        """
        self.metrics = metrics or PrometheusMetrics()
        self.logger = get_logger('performance_monitor')
    
    def monitor_function(self, name: str):
        """
        Decorador para monitorear función
        
        Args:
            name: Nombre de la función
            
        Returns:
            Decorador
        """
        def decorator(f):
            def wrapper(*args, **kwargs):
                import time
                start_time = time.time()
                
                try:
                    result = f(*args, **kwargs)
                    duration = time.time() - start_time
                    self.logger.info(f"Función {name} completada en {duration:.2f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.logger.error(f"Función {name} falló en {duration:.2f}s: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def track_memory_usage(self):
        """Rastrear uso de memoria"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    
    def track_cpu_usage(self):
        """Rastrear uso de CPU"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        return {
            'percent': process.cpu_percent(),
            'num_threads': process.num_threads()
        }
