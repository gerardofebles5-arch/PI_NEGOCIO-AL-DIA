"""
Paquete de tareas para (π)NAD
"""

from .celery_tasks import celery_app, TaskManager

__all__ = ['celery_app', 'TaskManager']
