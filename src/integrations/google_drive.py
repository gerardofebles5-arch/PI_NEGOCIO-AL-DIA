"""
Módulo de integración con Google Drive para (π)NAD
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Dict, List, Optional
import os


class GoogleDriveIntegration:
    """Integración con Google Drive API para (π)NAD"""
    
    def __init__(self, credentials_path: str = None):
        """
        Inicializar integración con Google Drive
        
        Args:
            credentials_path: Ruta al archivo de credenciales JSON de service account
        """
        self.credentials_path = credentials_path
        self.drive_service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar servicio de Google Drive"""
        try:
            if self.credentials_path:
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
            else:
                # Usar credenciales por defecto (para desarrollo)
                creds = service_account.Credentials.from_service_account_file(
                    'config/service_account.json',
                    scopes=['https://www.googleapis.com/auth/drive']
                )
            
            self.drive_service = build('drive', 'v3', credentials=creds)
            print("Google Drive service inicializado exitosamente")
        except Exception as e:
            print(f"Error inicializando Google Drive service: {e}")
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Dict:
        """
        Crear carpeta en Google Drive
        
        Args:
            folder_name: Nombre de la carpeta
            parent_folder_id: ID de la carpeta padre (opcional)
            
        Returns:
            Diccionario con información de la carpeta creada
        """
        if not self.drive_service:
            return {'error': 'Drive service no inicializado'}
        
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return {
                'folder_id': folder['id'],
                'folder_name': folder_name,
                'parent_id': parent_folder_id
            }
        except Exception as e:
            return {'error': str(e)}
    
    def create_pinad_structure(self, root_folder_name: str = 'PINAD') -> Dict:
        """
        Crear estructura de carpetas para (π)NAD
        
        Args:
            root_folder_name: Nombre de la carpeta raíz
            
        Returns:
            Diccionario con información de las carpetas creadas
        """
        # Crear carpeta raíz
        root_folder = self.create_folder(root_folder_name)
        
        if 'error' in root_folder:
            return root_folder
        
        root_folder_id = root_folder['folder_id']
        
        # Crear subcarpetas principales
        subfolders = [
            '01_Clients',
            '02_Templates',
            '03_Processing',
            '04_Reports',
            '05_Logs',
            '06_Configuration'
        ]
        
        created_folders = {}
        for folder_name in subfolders:
            folder = self.create_folder(folder_name, root_folder_id)
            created_folders[folder_name] = folder
        
        return {
            'root_folder': root_folder,
            'subfolders': created_folders
        }
    
    def create_client_folder(self, client_data: Dict, root_folder_id: str = None) -> Dict:
        """
        Crear estructura de carpetas para un cliente
        
        Args:
            client_data: Datos del cliente (rif, name, email)
            root_folder_id: ID de la carpeta raíz de clientes
            
        Returns:
            Diccionario con información de las carpetas creadas
        """
        # Crear carpeta del cliente
        client_folder_name = f"{client_data['rif']} - {client_data['name']}"
        client_folder = self.create_folder(client_folder_name, root_folder_id)
        
        if 'error' in client_folder:
            return client_folder
        
        client_folder_id = client_folder['folder_id']
        
        # Crear subcarpetas del cliente
        subfolders = ['Originals', 'Processed', 'Validated', 'Archive']
        created_subfolders = {}
        
        for folder_name in subfolders:
            folder = self.create_folder(folder_name, client_folder_id)
            created_subfolders[folder_name] = folder
        
        # Compartir con cliente
        if 'email' in client_data:
            self.share_folder(client_folder_id, client_data['email'], 'writer')
        
        return {
            'client_folder': client_folder,
            'subfolders': created_subfolders
        }
    
    def upload_file(self, file_path: str, folder_id: str, 
                   file_name: str = None) -> Dict:
        """
        Subir archivo a Google Drive
        
        Args:
            file_path: Ruta del archivo local
            folder_id: ID de la carpeta destino
            file_name: Nombre del archivo en Drive (opcional)
            
        Returns:
            Diccionario con información del archivo subido
        """
        if not self.drive_service:
            return {'error': 'Drive service no inicializado'}
        
        try:
            file_metadata = {
                'name': file_name or os.path.basename(file_path),
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return {
                'file_id': file['id'],
                'file_name': file_metadata['name'],
                'folder_id': folder_id
            }
        except Exception as e:
            return {'error': str(e)}
    
    def share_folder(self, folder_id: str, email: str, role: str = 'writer') -> Dict:
        """
        Compartir carpeta con usuario
        
        Args:
            folder_id: ID de la carpeta
            email: Email del usuario
            role: Rol (reader, writer, commenter)
            
        Returns:
            Diccionario con resultado de la operación
        """
        if not self.drive_service:
            return {'error': 'Drive service no inicializado'}
        
        try:
            permission_metadata = {
                'role': role,
                'type': 'user',
                'emailAddress': email
            }
            
            permission = self.drive_service.permissions().create(
                fileId=folder_id,
                body=permission_metadata,
                fields='id'
            ).execute()
            
            return {
                'permission_id': permission['id'],
                'email': email,
                'role': role
            }
        except Exception as e:
            return {'error': str(e)}
    
    def list_files_in_folder(self, folder_id: str) -> Dict:
        """
        Listar archivos en una carpeta
        
        Args:
            folder_id: ID de la carpeta
            
        Returns:
            Diccionario con lista de archivos
        """
        if not self.drive_service:
            return {'error': 'Drive service no inicializado'}
        
        try:
            results = self.drive_service.files().list(
                q=f"'{folder_id}' in parents",
                fields='files(id, name, mimeType, size, createdTime)'
            ).execute()
            
            files = results.get('files', [])
            
            return {
                'folder_id': folder_id,
                'files': files,
                'total': len(files)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_file(self, file_id: str) -> Dict:
        """
        Obtener información de un archivo
        
        Args:
            file_id: ID del archivo
            
        Returns:
            Diccionario con información del archivo
        """
        if not self.drive_service:
            return {'error': 'Drive service no inicializado'}
        
        try:
            file = self.drive_service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,size,createdTime,parents'
            ).execute()
            
            return file
        except Exception as e:
            return {'error': str(e)}
    
    def delete_file(self, file_id: str) -> Dict:
        """
        Eliminar archivo
        
        Args:
            file_id: ID del archivo
            
        Returns:
            Diccionario con resultado de la operación
        """
        if not self.drive_service:
            return {'error': 'Drive service no inicializado'}
        
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            
            return {
                'success': True,
                'file_id': file_id
            }
        except Exception as e:
            return {'error': str(e)}
    
    def move_file(self, file_id: str, new_folder_id: str) -> Dict:
        """
        Mover archivo a otra carpeta
        
        Args:
            file_id: ID del archivo
            new_folder_id: ID de la nueva carpeta
            
        Returns:
            Diccionario con resultado de la operación
        """
        if not self.drive_service:
            return {'error': 'Drive service no inicializado'}
        
        try:
            # Obtener archivo actual
            file = self.get_file(file_id)
            
            if 'error' in file:
                return file
            
            # Actualizar padres
            self.drive_service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=file['parents'][0] if file['parents'] else None
            ).execute()
            
            return {
                'success': True,
                'file_id': file_id,
                'new_folder_id': new_folder_id
            }
        except Exception as e:
            return {'error': str(e)}


# Importar MediaFileUpload al final para evitar dependencias circulares
from googleapiclient.http import MediaFileUpload
