"""
Metrics Collector para (π)NAD V6.0
Colección de métricas de aplicación y sistema
"""

import time
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from functools import wraps

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Métrica base"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir métrica a diccionario"""
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'description': self.description,
        }


class MetricsCollector:
    """
    Colector de métricas
    Implementa patrones de métricas (Counter, Gauge, Histogram, Summary)
    """
    
    def __init__(self, enable_auto_flush: bool = True, flush_interval: int = 60):
        """
        Inicializar colector de métricas
        
        Args:
            enable_auto_flush: Habilitar flush automático
            flush_interval: Intervalo de flush en segundos
        """
        self.enable_auto_flush = enable_auto_flush
        self.flush_interval = flush_interval
        
        # Almacenamiento de métricas
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._summaries: Dict[str, List[float]] = defaultdict(list)
        
        # Metadata de métricas
        self._metric_descriptions: Dict[str, str] = {}
        self._metric_labels: Dict[str, Dict[str, str]] = {}
        
        logger.info("MetricsCollector inicializado")
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Registrar métrica
        
        Args:
            name: Nombre de la métrica
            metric_type: Tipo de métrica
            description: Descripción de la métrica
            labels: Labels de la métrica
        """
        self._metric_descriptions[name] = description
        if labels:
            self._metric_labels[name] = labels
        
        # Inicializar estructura según tipo
        if metric_type == MetricType.COUNTER:
            self._counters[name] = 0.0
        elif metric_type == MetricType.GAUGE:
            self._gauges[name] = 0.0
        elif metric_type == MetricType.HISTOGRAM:
            self._histograms[name] = []
        elif metric_type == MetricType.SUMMARY:
            self._summaries[name] = []
        
        logger.debug(f"Métrica registrada: {name} ({metric_type.value})")
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Incrementar contador
        
        Args:
            name: Nombre del contador
            value: Valor a incrementar
            labels: Labels adicionales
        """
        if name not in self._counters:
            self.register_metric(name, MetricType.COUNTER)
        
        self._counters[name] += value
        
        if labels:
            key = self._get_labeled_name(name, labels)
            self._counters[key] = self._counters.get(key, 0.0) + value
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Establecer valor de gauge
        
        Args:
            name: Nombre del gauge
            value: Valor a establecer
            labels: Labels adicionales
        """
        if name not in self._gauges:
            self.register_metric(name, MetricType.GAUGE)
        
        self._gauges[name] = value
        
        if labels:
            key = self._get_labeled_name(name, labels)
            self._gauges[key] = value
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Observar valor en histograma
        
        Args:
            name: Nombre del histograma
            value: Valor a observar
            labels: Labels adicionales
        """
        if name not in self._histograms:
            self.register_metric(name, MetricType.HISTOGRAM)
        
        self._histograms[name].append(value)
        
        if labels:
            key = self._get_labeled_name(name, labels)
            self._histograms[key].append(value)
    
    def observe_summary(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Observar valor en summary
        
        Args:
            name: Nombre del summary
            value: Valor a observar
            labels: Labels adicionales
        """
        if name not in self._summaries:
            self.register_metric(name, MetricType.SUMMARY)
        
        self._summaries[name].append(value)
        
        if labels:
            key = self._get_labeled_name(name, labels)
            self._summaries[key].append(value)
    
    def get_counter(self, name: str) -> float:
        """
        Obtener valor de contador
        
        Args:
            name: Nombre del contador
            
        Returns:
            Valor del contador
        """
        return self._counters.get(name, 0.0)
    
    def get_gauge(self, name: str) -> Optional[float]:
        """
        Obtener valor de gauge
        
        Args:
            name: Nombre del gauge
            
        Returns:
            Valor del gauge o None
        """
        return self._gauges.get(name)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """
        Obtener estadísticas de histograma
        
        Args:
            name: Nombre del histograma
            
        Returns:
            Estadísticas del histograma
        """
        values = self._histograms.get(name, [])
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            'count': n,
            'sum': sum(sorted_values),
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'mean': sum(sorted_values) / n,
            'p50': sorted_values[int(n * 0.5)],
            'p90': sorted_values[int(n * 0.9)],
            'p95': sorted_values[int(n * 0.95)],
            'p99': sorted_values[int(n * 0.99)],
        }
    
    def get_summary_stats(self, name: str) -> Dict[str, float]:
        """
        Obtener estadísticas de summary
        
        Args:
            name: Nombre del summary
            
        Returns:
            Estadísticas del summary
        """
        return self.get_histogram_stats(name)
    
    def get_all_metrics(self) -> List[Metric]:
        """
        Obtener todas las métricas
        
        Returns:
            Lista de métricas
        """
        metrics = []
        
        # Counters
        for name, value in self._counters.items():
            metrics.append(Metric(
                name=name,
                metric_type=MetricType.COUNTER,
                value=value,
                description=self._metric_descriptions.get(name, ""),
                labels=self._metric_labels.get(name, {}),
            ))
        
        # Gauges
        for name, value in self._gauges.items():
            metrics.append(Metric(
                name=name,
                metric_type=MetricType.GAUGE,
                value=value,
                description=self._metric_descriptions.get(name, ""),
                labels=self._metric_labels.get(name, {}),
            ))
        
        # Histograms
        for name, values in self._histograms.items():
            stats = self.get_histogram_stats(name)
            metrics.append(Metric(
                name=f"{name}_count",
                metric_type=MetricType.COUNTER,
                value=stats.get('count', 0),
                description=f"Count for {name}",
                labels=self._metric_labels.get(name, {}),
            ))
        
        # Summaries
        for name, values in self._summaries.items():
            stats = self.get_summary_stats(name)
            metrics.append(Metric(
                name=f"{name}_count",
                metric_type=MetricType.COUNTER,
                value=stats.get('count', 0),
                description=f"Count for {name}",
                labels=self._metric_labels.get(name, {}),
            ))
        
        return metrics
    
    def reset_metric(self, name: str) -> None:
        """
        Resetear métrica
        
        Args:
            name: Nombre de la métrica
        """
        if name in self._counters:
            self._counters[name] = 0.0
        if name in self._gauges:
            self._gauges[name] = 0.0
        if name in self._histograms:
            self._histograms[name] = []
        if name in self._summaries:
            self._summaries[name] = []
        
        logger.debug(f"Métrica reseteada: {name}")
    
    def reset_all_metrics(self) -> None:
        """Resetear todas las métricas"""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._summaries.clear()
        logger.info("Todas las métricas reseteadas")
    
    def _get_labeled_name(self, name: str, labels: Dict[str, str]) -> str:
        """
        Generar nombre con labels
        
        Args:
            name: Nombre base
            labels: Labels
            
        Returns:
            Nombre con labels
        """
        label_str = ','.join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"


def track_time(metric_name: str, collector: MetricsCollector):
    """
    Decorador para trackear tiempo de ejecución
    
    Args:
        metric_name: Nombre de la métrica
        collector: Colector de métricas
        
    Returns:
        Función decorada
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                collector.observe_histogram(metric_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                collector.observe_histogram(metric_name, duration)
                raise
        return wrapper
    return decorator


def track_calls(metric_name: str, collector: MetricsCollector):
    """
    Decorador para trackear llamadas a función
    
    Args:
        metric_name: Nombre de la métrica
        collector: Colector de métricas
        
    Returns:
        Función decorada
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            collector.increment_counter(metric_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator
