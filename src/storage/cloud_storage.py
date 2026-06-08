"""
Sistema de archivos con Google Cloud Storage para (π)NAD
"""

from google.cloud import storage
from google.cloud.storage import Blob
from typing import Dict, List, Optional
from datetime import datetime
import os
from src.utils.logger import get_logger
from src.utils.exceptions import FileException


class CloudStorageManager:
    """Gestor de almacenamiento en Google Cloud Storage"""
    
    def __init__(self, bucket_name: str = None, credentials_path: str = None):
        """
        Inicializar gestor de Cloud Storage
        
        Args:
            bucket_name: Nombre del bucket
            credentials_path: Ruta al archivo de credenciales
        """
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME', 'pinad-storage')
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.logger = get_logger('cloud_storage')
        
        self.client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar cliente de Cloud Storage"""
        try:
            if self.credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            
            # Verificar que el bucket existe
            if not self.bucket.exists():
                self.logger.warning(f"Bucket {self.bucket_name} no existe, intentando crear...")
                self.bucket = self.client.create_bucket(self.bucket_name)
            
            self.logger.info(f"Cloud Storage inicializado: {self.bucket_name}")
        except Exception as e:
            self.logger.error(f"Error inicializando Cloud Storage: {e}")
            raise FileException(f"Error inicializando Cloud Storage: {e}")
    
    def upload_file(self, file_path: str, destination_blob_name: str, 
                   content_type: str = None, metadata: Dict = None) -> Dict:
        """
        Subir archivo a Cloud Storage
        
        Args:
            file_path: Ruta del archivo local
            destination_blob_name: Nombre del blob destino
            content_type: Tipo de contenido
            metadata: Metadatos del archivo
            
        Returns:
            Información del archivo subido
        """
        try:
            blob = self.bucket.blob(destination_blob_name)
            
            # Configurar tipo de contenido
            if content_type:
                blob.content_type = content_type
            
            # Configurar metadatos
            if metadata:
                blob.metadata = metadata
            
            # Subir archivo
            blob.upload_from_filename(file_path)
            
            # Obtener URL pública
            public_url = blob.public_url
            
            self.logger.info(f"Archivo subido: {destination_blob_name}")
            
            return {
                'blob_name': destination_blob_name,
                'public_url': public_url,
                'size': blob.size,
                'content_type': blob.content_type,
                'time_created': blob.time_created,
                'md5_hash': blob.md5_hash
            }
        except Exception as e:
            self.logger.error(f"Error subiendo archivo: {e}")
            raise FileException(f"Error subiendo archivo: {e}", file_path=file_path)
    
    def upload_bytes(self, data: bytes, destination_blob_name: str,
                    content_type: str = None, metadata: Dict = None) -> Dict:
        """
        Subir bytes a Cloud Storage
        
        Args:
            data: Datos a subir
            destination_blob_name: Nombre del blob destino
            content_type: Tipo de contenido
            metadata: Metadatos del archivo
            
        Returns:
            Información del archivo subido
        """
        try:
            blob = self.bucket.blob(destination_blob_name)
            
            if content_type:
                blob.content_type = content_type
            
            if metadata:
                blob.metadata = metadata
            
            blob.upload_from_string(data)
            
            public_url = blob.public_url
            
            self.logger.info(f"Bytes subidos: {destination_blob_name}")
            
            return {
                'blob_name': destination_blob_name,
                'public_url': public_url,
                'size': blob.size,
                'content_type': blob.content_type,
                'time_created': blob.time_created
            }
        except Exception as e:
            self.logger.error(f"Error subiendo bytes: {e}")
            raise FileException(f"Error subiendo bytes: {e}")
    
    def download_file(self, blob_name: str, destination_file_path: str) -> Dict:
        """
        Descargar archivo de Cloud Storage
        
        Args:
            blob_name: Nombre del blob
            destination_file_path: Ruta destino local
            
        Returns:
            Información del archivo descargado
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileException(f"Blob no existe: {blob_name}")
            
            blob.download_to_filename(destination_file_path)
            
            self.logger.info(f"Archivo descargado: {blob_name}")
            
            return {
                'blob_name': blob_name,
                'destination_path': destination_file_path,
                'size': blob.size,
                'content_type': blob.content_type
            }
        except Exception as e:
            self.logger.error(f"Error descargando archivo: {e}")
            raise FileException(f"Error descargando archivo: {e}")
    
    def download_bytes(self, blob_name: str) -> bytes:
        """
        Descargar bytes de Cloud Storage
        
        Args:
            blob_name: Nombre del blob
            
        Returns:
            Datos del blob
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileException(f"Blob no existe: {blob_name}")
            
            data = blob.download_as_bytes()
            
            self.logger.info(f"Bytes descargados: {blob_name}")
            
            return data
        except Exception as e:
            self.logger.error(f"Error descargando bytes: {e}")
            raise FileException(f"Error descargando bytes: {e}")
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Eliminar archivo de Cloud Storage
        
        Args:
            blob_name: Nombre del blob
            
        Returns:
            True si exitoso
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                self.logger.warning(f"Blob no existe: {blob_name}")
                return False
            
            blob.delete()
            
            self.logger.info(f"Archivo eliminado: {blob_name}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando archivo: {e}")
            raise FileException(f"Error eliminando archivo: {e}")
    
    def list_files(self, prefix: str = None, delimiter: str = None) -> List[Dict]:
        """
        Listar archivos en bucket
        
        Args:
            prefix: Prefijo para filtrar
            delimiter: Delimitador para agrupar
            
        Returns:
            Lista de archivos
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
            
            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'time_created': blob.time_created,
                    'updated': blob.updated,
                    'public_url': blob.public_url
                })
            
            self.logger.info(f"Archivos listados: {len(files)}")
            
            return files
        except Exception as e:
            self.logger.error(f"Error listando archivos: {e}")
            raise FileException(f"Error listando archivos: {e}")
    
    def get_file_info(self, blob_name: str) -> Dict:
        """
        Obtener información de archivo
        
        Args:
            blob_name: Nombre del blob
            
        Returns:
            Información del archivo
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileException(f"Blob no existe: {blob_name}")
            
            blob.reload()
            
            return {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'time_created': blob.time_created,
                'updated': blob.updated,
                'md5_hash': blob.md5_hash,
                'public_url': blob.public_url,
                'metadata': blob.metadata
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo información: {e}")
            raise FileException(f"Error obteniendo información: {e}")
    
    def generate_signed_url(self, blob_name: str, expiration: int = 3600) -> str:
        """
        Generar URL firmada para acceso temporal
        
        Args:
            blob_name: Nombre del blob
            expiration: Tiempo de expiración en segundos
            
        Returns:
            URL firmada
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileException(f"Blob no existe: {blob_name}")
            
            url = blob.generate_signed_url(expiration=expiration)
            
            self.logger.info(f"URL firmada generada: {blob_name}")
            
            return url
        except Exception as e:
            self.logger.error(f"Error generando URL firmada: {e}")
            raise FileException(f"Error generando URL firmada: {e}")
    
    def copy_file(self, source_blob_name: str, destination_blob_name: str) -> Dict:
        """
        Copiar archivo dentro del bucket
        
        Args:
            source_blob_name: Nombre del blob origen
            destination_blob_name: Nombre del blob destino
            
        Returns:
            Información del archivo copiado
        """
        try:
            source_blob = self.bucket.blob(source_blob_name)
            destination_blob = self.bucket.blob(destination_blob_name)
            
            if not source_blob.exists():
                raise FileException(f"Blob origen no existe: {source_blob_name}")
            
            destination_blob.copy_from(source_blob)
            
            self.logger.info(f"Archivo copiado: {source_blob_name} -> {destination_blob_name}")
            
            return {
                'source': source_blob_name,
                'destination': destination_blob_name,
                'size': destination_blob.size
            }
        except Exception as e:
            self.logger.error(f"Error copiando archivo: {e}")
            raise FileException(f"Error copiando archivo: {e}")
    
    def move_file(self, source_blob_name: str, destination_blob_name: str) -> Dict:
        """
        Mover archivo dentro del bucket
        
        Args:
            source_blob_name: Nombre del blob origen
            destination_blob_name: Nombre del blob destino
            
        Returns:
            Información del archivo movido
        """
        try:
            # Copiar archivo
            result = self.copy_file(source_blob_name, destination_blob_name)
            
            # Eliminar origen
            self.delete_file(source_blob_name)
            
            self.logger.info(f"Archivo movido: {source_blob_name} -> {destination_blob_name}")
            
            return result
        except Exception as e:
            self.logger.error(f"Error moviendo archivo: {e}")
            raise FileException(f"Error moviendo archivo: {e}")
    
    def get_bucket_info(self) -> Dict:
        """
        Obtener información del bucket
        
        Returns:
            Información del bucket
        """
        try:
            self.bucket.reload()
            
            return {
                'name': self.bucket.name,
                'location': self.bucket.location,
                'storage_class': self.bucket.storage_class,
                'created': self.bucket.time_created,
                'size': self.bucket.size
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo información del bucket: {e}")
            raise FileException(f"Error obteniendo información del bucket: {e}")


class StoragePathBuilder:
    """Constructor de rutas de almacenamiento"""
    
    @staticmethod
    def client_document_path(client_id: str, document_id: str, file_name: str) -> str:
        """Construir ruta para documento de cliente"""
        return f"clients/{client_id}/documents/{document_id}/{file_name}"
    
    @staticmethod
    def client_original_path(client_id: str, document_id: str, file_name: str) -> str:
        """Construir ruta para archivo original de cliente"""
        return f"clients/{client_id}/originals/{document_id}/{file_name}"
    
    @staticmethod
    def client_processed_path(client_id: str, document_id: str, file_name: str) -> str:
        """Construir ruta para archivo procesado de cliente"""
        return f"clients/{client_id}/processed/{document_id}/{file_name}"
    
    @staticmethod
    def client_validated_path(client_id: str, document_id: str, file_name: str) -> str:
        """Construir ruta para archivo validado de cliente"""
        return f"clients/{client_id}/validated/{document_id}/{file_name}"
    
    @staticmethod
    def dashboard_path(client_id: str, period: str, format: str) -> str:
        """Construir ruta para dashboard exportado"""
        return f"clients/{client_id}/dashboards/{period}/dashboard.{format}"
    
    @staticmethod
    def report_path(client_id: str, report_type: str, date: str) -> str:
        """Construir ruta para reporte"""
        return f"clients/{client_id}/reports/{report_type}/{date}/report.pdf"
    
    @staticmethod
    def temp_path(file_name: str) -> str:
        """Construir ruta para archivo temporal"""
        return f"temp/{datetime.now().strftime('%Y/%m/%d')}/{file_name}"
    
    @staticmethod
    def log_path(log_type: str, date: str) -> str:
        """Construir ruta para log"""
        return f"logs/{log_type}/{date}/log.txt"
