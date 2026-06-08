"""
Sistema de notificaciones en tiempo real para (π)NAD
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask import request
from typing import Dict, List, Optional
from datetime import datetime
from src.utils.logger import get_logger
import json


class RealtimeNotificationManager:
    """Gestor de notificaciones en tiempo real con SocketIO"""
    
    def __init__(self, app=None, cors_allowed_origins="*"):
        """
        Inicializar gestor de notificaciones en tiempo real
        
        Args:
            app: Aplicación Flask
            cors_allowed_origins: Orígenes permitidos para CORS
        """
        self.logger = get_logger('realtime_notifications')
        self.socketio = SocketIO(
            cors_allowed_origins=cors_allowed_origins,
            async_mode='threading',
            logger=True,
            engineio_logger=False
        )
        
        if app:
            self.init_app(app)
        
        self.connected_clients = {}  # {sid: client_info}
        self.client_rooms = {}  # {client_id: [sids]}
    
    def init_app(self, app):
        """
        Inicializar con aplicación Flask
        
        Args:
            app: Aplicación Flask
        """
        self.socketio.init_app(app, cors_allowed_origins="*")
        self._setup_event_handlers()
        self.logger.info("Sistema de notificaciones en tiempo real inicializado")
    
    def _setup_event_handlers(self):
        """Configurar manejadores de eventos SocketIO"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Manejar conexión de cliente"""
            sid = request.sid
            self.connected_clients[sid] = {
                'connected_at': datetime.now().isoformat(),
                'user_agent': request.headers.get('User-Agent', '')
            }
            self.logger.info(f"Cliente conectado: {sid}")
            emit('connected', {'sid': sid, 'timestamp': datetime.now().isoformat()})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Manejar desconexión de cliente"""
            sid = request.sid
            if sid in self.connected_clients:
                del self.connected_clients[sid]
            self.logger.info(f"Cliente desconectado: {sid}")
        
        @self.socketio.on('join_client_room')
        def handle_join_client_room(data):
            """
            Manejar unión a sala de cliente
            
            Args:
                data: {'client_id': str}
            """
            sid = request.sid
            client_id = data.get('client_id')
            
            if client_id:
                room = f"client_{client_id}"
                join_room(room)
                
                # Registrar cliente en sala
                if client_id not in self.client_rooms:
                    self.client_rooms[client_id] = []
                self.client_rooms[client_id].append(sid)
                
                self.logger.info(f"Cliente {sid} se unió a sala {room}")
                emit('joined_room', {'room': room, 'client_id': client_id})
        
        @self.socketio.on('leave_client_room')
        def handle_leave_client_room(data):
            """
            Manejar salida de sala de cliente
            
            Args:
                data: {'client_id': str}
            """
            sid = request.sid
            client_id = data.get('client_id')
            
            if client_id:
                room = f"client_{client_id}"
                leave_room(room)
                
                # Remover cliente de sala
                if client_id in self.client_rooms and sid in self.client_rooms[client_id]:
                    self.client_rooms[client_id].remove(sid)
                
                self.logger.info(f"Cliente {sid} salió de sala {room}")
                emit('left_room', {'room': room, 'client_id': client_id})
        
        @self.socketio.on('ping')
        def handle_ping():
            """Manejar ping de cliente"""
            emit('pong', {'timestamp': datetime.now().isoformat()})
    
    def notify_client(self, client_id: str, notification_type: str, data: Dict):
        """
        Enviar notificación a cliente específico
        
        Args:
            client_id: ID del cliente
            notification_type: Tipo de notificación
            data: Datos de la notificación
        """
        room = f"client_{client_id}"
        notification = {
            'type': notification_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('notification', notification, room=room)
        self.logger.info(f"Notificación enviada a cliente {client_id}: {notification_type}")
    
    def notify_validator(self, validator_id: str, notification_type: str, data: Dict):
        """
        Enviar notificación a asesor específico
        
        Args:
            validator_id: ID del asesor
            notification_type: Tipo de notificación
            data: Datos de la notificación
        """
        room = f"validator_{validator_id}"
        notification = {
            'type': notification_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('notification', notification, room=room)
        self.logger.info(f"Notificación enviada a asesor {validator_id}: {notification_type}")
    
    def broadcast_to_all(self, notification_type: str, data: Dict):
        """
        Enviar notificación a todos los clientes conectados
        
        Args:
            notification_type: Tipo de notificación
            data: Datos de la notificación
        """
        notification = {
            'type': notification_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('notification', notification, broadcast=True)
        self.logger.info(f"Notificación broadcast: {notification_type}")
    
    def notify_document_processed(self, client_id: str, document_id: str, success: bool):
        """
        Notificar que documento fue procesado
        
        Args:
            client_id: ID del cliente
            document_id: ID del documento
            success: Si el procesamiento fue exitoso
        """
        self.notify_client(
            client_id,
            'document_processed',
            {
                'document_id': document_id,
                'success': success,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def notify_validation_completed(self, client_id: str, validation_id: str, action: str):
        """
        Notificar que validación fue completada
        
        Args:
            client_id: ID del cliente
            validation_id: ID de la validación
            action: Acción tomada (approve, reject, observe)
        """
        self.notify_client(
            client_id,
            'validation_completed',
            {
                'validation_id': validation_id,
                'action': action,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def notify_new_validation(self, validator_id: str, validation_id: str, client_id: str):
        """
        Notificar a asesor sobre nueva validación
        
        Args:
            validator_id: ID del asesor
            validation_id: ID de la validación
            client_id: ID del cliente
        """
        self.notify_validator(
            validator_id,
            'new_validation',
            {
                'validation_id': validation_id,
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def notify_dashboard_updated(self, client_id: str, period: str):
        """
        Notificar que dashboard fue actualizado
        
        Args:
            client_id: ID del cliente
            period: Período del dashboard
        """
        self.notify_client(
            client_id,
            'dashboard_updated',
            {
                'period': period,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def notify_system_maintenance(self, message: str):
        """
        Notificar mantenimiento del sistema
        
        Args:
            message: Mensaje de mantenimiento
        """
        self.broadcast_to_all(
            'system_maintenance',
            {
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def get_connected_clients_count(self) -> int:
        """
        Obtener número de clientes conectados
        
        Returns:
            Número de clientes conectados
        """
        return len(self.connected_clients)
    
    def get_client_room_count(self, client_id: str) -> int:
        """
        Obtener número de conexiones en sala de cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Número de conexiones en sala
        """
        return len(self.client_rooms.get(client_id, []))
    
    def run(self, host: str = '0.0.0.0', port: int = 5001, debug: bool = False):
        """
        Ejecutar servidor SocketIO
        
        Args:
            host: Host del servidor
            port: Puerto del servidor
            debug: Modo debug
        """
        self.logger.info(f"Iniciando servidor SocketIO en {host}:{port}")
        self.socketio.run(None, host=host, port=port, debug=debug)


class NotificationTypes:
    """Tipos de notificaciones disponibles"""
    
    # Documentos
    DOCUMENT_UPLOADED = 'document_uploaded'
    DOCUMENT_PROCESSING = 'document_processing'
    DOCUMENT_PROCESSED = 'document_processed'
    DOCUMENT_ERROR = 'document_error'
    
    # Validaciones
    VALIDATION_REQUESTED = 'validation_requested'
    VALIDATION_ASSIGNED = 'validation_assigned'
    VALIDATION_COMPLETED = 'validation_completed'
    
    # Transacciones
    TRANSACTION_CREATED = 'transaction_created'
    TRANSACTION_VALIDATED = 'transaction_validated'
    
    # Dashboards
    DASHBOARD_UPDATED = 'dashboard_updated'
    DASHBOARD_GENERATED = 'dashboard_generated'
    
    # Sistema
    SYSTEM_MAINTENANCE = 'system_maintenance'
    SYSTEM_ERROR = 'system_error'
    SYSTEM_ANNOUNCEMENT = 'system_announcement'
    
    # Seguridad
    LOGIN_SUCCESS = 'login_success'
    LOGIN_FAILED = 'login_failed'
    PASSWORD_CHANGED = 'password_changed'


class NotificationBuilder:
    """Constructor de notificaciones"""
    
    @staticmethod
    def document_uploaded(document_id: str, file_name: str) -> Dict:
        """Notificación de documento subido"""
        return {
            'title': 'Documento Subido',
            'message': f'El documento "{file_name}" ha sido subido exitosamente',
            'document_id': document_id,
            'file_name': file_name
        }
    
    @staticmethod
    def document_processed(document_id: str, success: bool, confidence: float = None) -> Dict:
        """Notificación de documento procesado"""
        if success:
            message = f'Documento procesado exitosamente'
            if confidence:
                message += f' (confianza: {confidence:.2%})'
        else:
            message = 'Error procesando documento'
        
        return {
            'title': 'Procesamiento Completado',
            'message': message,
            'document_id': document_id,
            'success': success,
            'confidence': confidence
        }
    
    @staticmethod
    def validation_completed(validation_id: str, action: str, notes: str = None) -> Dict:
        """Notificación de validación completada"""
        action_messages = {
            'approve': 'Tu transacción ha sido aprobada',
            'reject': 'Tu transacción ha sido rechazada',
            'observe': 'Tu transacción requiere observación'
        }
        
        return {
            'title': 'Validación Completada',
            'message': action_messages.get(action, 'Validación completada'),
            'validation_id': validation_id,
            'action': action,
            'notes': notes
        }
    
    @staticmethod
    def new_validation(validation_id: str, client_name: str) -> Dict:
        """Notificación de nueva validación para asesor"""
        return {
            'title': 'Nueva Validación Asignada',
            'message': f'Tienes una nueva validación de {client_name}',
            'validation_id': validation_id,
            'client_name': client_name
        }
    
    @staticmethod
    def dashboard_updated(period: str) -> Dict:
        """Notificación de dashboard actualizado"""
        return {
            'title': 'Dashboard Actualizado',
            'message': f'Tu dashboard del período {period} ha sido actualizado',
            'period': period
        }
    
    @staticmethod
    def system_maintenance(message: str) -> Dict:
        """Notificación de mantenimiento del sistema"""
        return {
            'title': 'Mantenimiento del Sistema',
            'message': message,
            'priority': 'high'
        }
