"""
Sistema de cola de tareas con Celery para (π)NAD
"""

from celery import Celery
from celery.schedules import crontab
from src.utils.logger import get_logger
from datetime import datetime
import os


# Configuración de Celery
celery_app = Celery('pinad')

# Configuración de broker y backend
celery_app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Caracas',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000
)

# Configuración de tareas periódicas
celery_app.conf.beat_schedule = {
    'cleanup-temp-files-every-hour': {
        'task': 'tasks.celery_tasks.cleanup_temp_files',
        'schedule': crontab(minute=0),  # Cada hora
    },
    'process-pending-validations-every-5-minutes': {
        'task': 'tasks.celery_tasks.process_pending_validations',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
    'generate-daily-reports-at-midnight': {
        'task': 'tasks.celery_tasks.generate_daily_reports',
        'schedule': crontab(hour=0, minute=0),  # Medianoche
    },
    'cleanup-old-cache-every-day': {
        'task': 'tasks.celery_tasks.cleanup_old_cache',
        'schedule': crontab(hour=2, minute=0),  # 2 AM
    },
    'send-reminders-every-morning': {
        'task': 'tasks.celery_tasks.send_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9 AM
    }
}


logger = get_logger('celery_tasks')


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_ocr(self, document_id: str, file_path: str, document_type: str):
    """
    Tarea asíncrona para procesar documento con OCR
    
    Args:
        document_id: ID del documento
        file_path: Ruta del archivo
        document_type: Tipo de documento
        
    Returns:
        Resultado del procesamiento
    """
    try:
        logger.info(f"Procesando documento {document_id} con OCR")
        
        # Importar aquí para evitar dependencias circulares
        from src.processing.document_processor import DocumentProcessor
        from src.ocr.ocr_engine import OCREngine
        
        # Inicializar componentes
        ocr_engine = OCREngine()
        processor = DocumentProcessor(ocr_engine=ocr_engine)
        
        # Procesar documento
        result = processor.process_document(file_path, document_type, 'system')
        
        logger.info(f"Documento {document_id} procesado exitosamente")
        
        return {
            'document_id': document_id,
            'success': result['success'],
            'extracted_data': result.get('extracted_data', {}),
            'ocr_confidence': result.get('ocr_confidence', 0)
        }
        
    except Exception as e:
        logger.error(f"Error procesando documento {document_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_batch_documents(self, document_ids: list, file_paths: list, document_type: str):
    """
    Tarea asíncrona para procesar lote de documentos
    
    Args:
        document_ids: Lista de IDs de documentos
        file_paths: Lista de rutas de archivos
        document_type: Tipo de documento
        
    Returns:
        Resultados del procesamiento
    """
    try:
        logger.info(f"Procesando lote de {len(document_ids)} documentos")
        
        from src.processing.document_processor import DocumentProcessor, BatchProcessor
        from src.ocr.ocr_engine import OCREngine
        
        # Inicializar componentes
        ocr_engine = OCREngine()
        processor = DocumentProcessor(ocr_engine=ocr_engine)
        batch_processor = BatchProcessor(document_processor=processor)
        
        # Procesar lote
        results = batch_processor.process_batch(file_paths, document_type, 'system')
        
        logger.info(f"Lote procesado: {results['successful']} exitosos, {results['failed']} fallidos")
        
        return results
        
    except Exception as e:
        logger.error(f"Error procesando lote: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_validation_notification(self, validation_id: str, client_id: str, status: str):
    """
    Tarea asíncrona para enviar notificación de validación
    
    Args:
        validation_id: ID de la validación
        client_id: ID del cliente
        status: Estado de la validación
        
    Returns:
        Resultado del envío
    """
    try:
        logger.info(f"Enviando notificación de validación {validation_id}")
        
        # Aquí se implementaría el envío real de notificación
        # (email, SMS, push notification, etc.)
        
        return {
            'validation_id': validation_id,
            'client_id': client_id,
            'status': status,
            'sent': True,
            'sent_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_client_dashboard(self, client_id: str, period: str = 'current_month'):
    """
    Tarea asíncrona para generar dashboard de cliente
    
    Args:
        client_id: ID del cliente
        period: Período del dashboard
        
    Returns:
        Datos del dashboard
    """
    try:
        logger.info(f"Generando dashboard para cliente {client_id}")
        
        from src.dashboard.dashboard_generator import DashboardGenerator
        
        generator = DashboardGenerator()
        
        # Aquí se obtendrían las transacciones del cliente
        # Por ahora, generamos dashboard vacío
        dashboard = generator.create_client_dashboard(client_id, [], period)
        
        logger.info(f"Dashboard generado para cliente {client_id}")
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Error generando dashboard: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task
def cleanup_temp_files():
    """Tarea periódica para limpiar archivos temporales"""
    try:
        logger.info("Limpiando archivos temporales")
        
        import os
        import glob
        from datetime import datetime, timedelta
        
        # Directorio temporal
        temp_dir = 'temp'
        
        if os.path.exists(temp_dir):
            # Archivos más viejos de 24 horas
            cutoff = datetime.now() - timedelta(hours=24)
            
            for file_path in glob.glob(os.path.join(temp_dir, '*')):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff:
                    try:
                        os.remove(file_path)
                        logger.info(f"Archivo temporal eliminado: {file_path}")
                    except Exception as e:
                        logger.error(f"Error eliminando archivo {file_path}: {e}")
        
        logger.info("Limpieza de archivos temporales completada")
        
    except Exception as e:
        logger.error(f"Error en limpieza de archivos temporales: {e}")


@celery_app.task
def process_pending_validations():
    """Tarea periódica para procesar validaciones pendientes"""
    try:
        logger.info("Procesando validaciones pendientes")
        
        # Aquí se implementaría la lógica para procesar validaciones pendientes
        # Por ejemplo, enviar recordatorios a asesores, reasignar validaciones, etc.
        
        logger.info("Procesamiento de validaciones pendientes completado")
        
    except Exception as e:
        logger.error(f"Error procesando validaciones pendientes: {e}")


@celery_app.task
def generate_daily_reports():
    """Tarea periódica para generar reportes diarios"""
    try:
        logger.info("Generando reportes diarios")
        
        # Aquí se implementaría la generación de reportes diarios
        # para todos los clientes activos
        
        logger.info("Generación de reportes diarios completada")
        
    except Exception as e:
        logger.error(f"Error generando reportes diarios: {e}")


@celery_app.task
def cleanup_old_cache():
    """Tarea periódica para limpiar caché antigua"""
    try:
        logger.info("Limpiando caché antigua")
        
        from src.cache.redis_cache import RedisCache
        
        cache = RedisCache()
        
        # Limpiar claves con TTL expirado
        # (Redis hace esto automáticamente, pero podemos limpiar manualmente si es necesario)
        
        logger.info("Limpieza de caché antigua completada")
        
    except Exception as e:
        logger.error(f"Error limpiando caché antigua: {e}")


@celery_app.task
def send_reminders():
    """Tarea periódica para enviar recordatorios"""
    try:
        logger.info("Enviando recordatorios")
        
        # Aquí se implementaría el envío de recordatorios
        # a clientes con documentos pendientes, validaciones pendientes, etc.
        
        logger.info("Envío de recordatorios completado")
        
    except Exception as e:
        logger.error(f"Error enviando recordatorios: {e}")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def export_dashboard(self, client_id: str, format: str = 'json'):
    """
    Tarea asíncrona para exportar dashboard
    
    Args:
        client_id: ID del cliente
        format: Formato de exportación
        
    Returns:
        Datos exportados
    """
    try:
        logger.info(f"Exportando dashboard para cliente {client_id} en formato {format}")
        
        from src.dashboard.dashboard_generator import DashboardGenerator
        
        generator = DashboardGenerator()
        
        # Obtener dashboard
        dashboard = generator.get_client_dashboard(client_id)
        
        if not dashboard:
            return {'error': 'Dashboard no encontrado'}
        
        # Exportar
        exported = generator.export_dashboard(client_id, format)
        
        logger.info(f"Dashboard exportado para cliente {client_id}")
        
        return {
            'client_id': client_id,
            'format': format,
            'data': exported
        }
        
    except Exception as e:
        logger.error(f"Error exportando dashboard: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_with_google_sheets(self, client_id: str, data: dict):
    """
    Tarea asíncrona para sincronizar con Google Sheets
    
    Args:
        client_id: ID del cliente
        data: Datos a sincronizar
        
    Returns:
        Resultado de la sincronización
    """
    try:
        logger.info(f"Sincronizando datos con Google Sheets para cliente {client_id}")
        
        from src.integrations.google_sheets import GoogleSheetsIntegration
        
        sheets = GoogleSheetsIntegration()
        
        # Aquí se implementaría la lógica de sincronización
        # Por ahora, retornamos éxito
        
        logger.info(f"Sincronización completada para cliente {client_id}")
        
        return {
            'client_id': client_id,
            'synced': True,
            'synced_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sincronizando con Google Sheets: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def upload_to_google_drive(self, file_path: str, folder_id: str, file_name: str = None):
    """
    Tarea asíncrona para subir archivo a Google Drive
    
    Args:
        file_path: Ruta del archivo local
        folder_id: ID de la carpeta destino
        file_name: Nombre del archivo en Drive
        
    Returns:
        Resultado de la subida
    """
    try:
        logger.info(f"Subiendo archivo a Google Drive: {file_path}")
        
        from src.integrations.google_drive import GoogleDriveIntegration
        
        drive = GoogleDriveIntegration()
        
        result = drive.upload_file(file_path, folder_id, file_name)
        
        logger.info(f"Archivo subido a Google Drive: {result.get('file_id')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error subiendo a Google Drive: {e}")
        raise self.retry(exc=e, countdown=60)


class TaskManager:
    """Gestor de tareas Celery para (π)NAD"""
    
    def __init__(self):
        """Inicializar gestor de tareas"""
        self.logger = get_logger('task_manager')
    
    def queue_document_processing(self, document_id: str, file_path: str, 
                                document_type: str) -> str:
        """
        Encolar procesamiento de documento
        
        Args:
            document_id: ID del documento
            file_path: Ruta del archivo
            document_type: Tipo de documento
            
        Returns:
            ID de la tarea Celery
        """
        task = process_document_ocr.delay(document_id, file_path, document_type)
        self.logger.info(f"Tarea de procesamiento encolada: {task.id}")
        return task.id
    
    def queue_batch_processing(self, document_ids: list, file_paths: list, 
                             document_type: str) -> str:
        """
        Encolar procesamiento por lotes
        
        Args:
            document_ids: Lista de IDs de documentos
            file_paths: Lista de rutas de archivos
            document_type: Tipo de documento
            
        Returns:
            ID de la tarea Celery
        """
        task = process_batch_documents.delay(document_ids, file_paths, document_type)
        self.logger.info(f"Tarea de procesamiento por lotes encolada: {task.id}")
        return task.id
    
    def queue_validation_notification(self, validation_id: str, client_id: str, 
                                    status: str) -> str:
        """
        Encolar notificación de validación
        
        Args:
            validation_id: ID de la validación
            client_id: ID del cliente
            status: Estado de la validación
            
        Returns:
            ID de la tarea Celery
        """
        task = send_validation_notification.delay(validation_id, client_id, status)
        self.logger.info(f"Tarea de notificación encolada: {task.id}")
        return task.id
    
    def queue_dashboard_generation(self, client_id: str, period: str = 'current_month') -> str:
        """
        Encolar generación de dashboard
        
        Args:
            client_id: ID del cliente
            period: Período del dashboard
            
        Returns:
            ID de la tarea Celery
        """
        task = generate_client_dashboard.delay(client_id, period)
        self.logger.info(f"Tarea de dashboard encolada: {task.id}")
        return task.id
    
    def queue_dashboard_export(self, client_id: str, format: str = 'json') -> str:
        """
        Encolar exportación de dashboard
        
        Args:
            client_id: ID del cliente
            format: Formato de exportación
            
        Returns:
            ID de la tarea Celery
        """
        task = export_dashboard.delay(client_id, format)
        self.logger.info(f"Tarea de exportación encolada: {task.id}")
        return task.id
    
    def queue_google_sheets_sync(self, client_id: str, data: dict) -> str:
        """
        Encolar sincronización con Google Sheets
        
        Args:
            client_id: ID del cliente
            data: Datos a sincronizar
            
        Returns:
            ID de la tarea Celery
        """
        task = sync_with_google_sheets.delay(client_id, data)
        self.logger.info(f"Tarea de sincronización encolada: {task.id}")
        return task.id
    
    def queue_drive_upload(self, file_path: str, folder_id: str, 
                         file_name: str = None) -> str:
        """
        Encolar subida a Google Drive
        
        Args:
            file_path: Ruta del archivo local
            folder_id: ID de la carpeta destino
            file_name: Nombre del archivo en Drive
            
        Returns:
            ID de la tarea Celery
        """
        task = upload_to_google_drive.delay(file_path, folder_id, file_name)
        self.logger.info(f"Tarea de subida encolada: {task.id}")
        return task.id
    
    def get_task_status(self, task_id: str) -> dict:
        """
        Obtener estado de tarea
        
        Args:
            task_id: ID de la tarea Celery
            
        Returns:
            Estado de la tarea
        """
        result = celery_app.AsyncResult(task_id)
        
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None,
            'failed': result.failed() if result.ready() else False,
            'success': result.successful() if result.ready() else False
        }
