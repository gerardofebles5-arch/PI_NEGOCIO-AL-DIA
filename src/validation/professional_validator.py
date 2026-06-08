"""
Módulo de validación profesional para (π)NAD
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid


class ProfessionalValidator:
    """Sistema de validación profesional para (π)NAD"""
    
    def __init__(self):
        """Inicializar sistema de validación profesional"""
        self.validators = {}  # {validator_id: validator_info}
        self.validations = {}  # {validation_id: validation_info}
        self.pending_validations = {}  # {client_id: [validation_ids]}
    
    def register_validator(self, validator_info: Dict) -> Dict:
        """
        Registrar un asesor contable
        
        Args:
            validator_info: Información del asesor
                - name: Nombre del asesor
                - email: Email del asesor
                - phone: Teléfono del asesor
                - specialization: Especialización
                - max_clients: Máximo de clientes asignados
            
        Returns:
            Diccionario con información del asesor registrado
        """
        validator_id = str(uuid.uuid4())
        
        validator_data = {
            'validator_id': validator_id,
            'name': validator_info.get('name', ''),
            'email': validator_info.get('email', ''),
            'phone': validator_info.get('phone', ''),
            'specialization': validator_info.get('specialization', 'general'),
            'max_clients': validator_info.get('max_clients', 50),
            'assigned_clients': [],
            'status': 'active',
            'registered_date': datetime.now().isoformat()
        }
        
        self.validators[validator_id] = validator_data
        
        return validator_data
    
    def assign_client_to_validator(self, client_id: str, validator_id: str) -> Dict:
        """
        Asignar cliente a asesor
        
        Args:
            client_id: ID del cliente
            validator_id: ID del asesor
            
        Returns:
            Diccionario con resultado de la asignación
        """
        if validator_id not in self.validators:
            return {'success': False, 'error': 'Asesor no encontrado'}
        
        validator = self.validators[validator_id]
        
        # Verificar si el asesor puede aceptar más clientes
        if len(validator['assigned_clients']) >= validator['max_clients']:
            return {'success': False, 'error': 'Asesor ha alcanzado máximo de clientes'}
        
        # Asignar cliente
        if client_id not in validator['assigned_clients']:
            validator['assigned_clients'].append(client_id)
        
        return {
            'success': True,
            'validator_id': validator_id,
            'client_id': client_id,
            'assigned_date': datetime.now().isoformat()
        }
    
    def create_validation_request(self, document_id: str, client_id: str, 
                                  extracted_data: Dict) -> Dict:
        """
        Crear solicitud de validación
        
        Args:
            document_id: ID del documento
            client_id: ID del cliente
            extracted_data: Datos extraídos del documento
            
        Returns:
            Diccionario con información de la solicitud de validación
        """
        validation_id = str(uuid.uuid4())
        
        # Encontrar asesor asignado al cliente
        validator_id = self._find_validator_for_client(client_id)
        
        validation_data = {
            'validation_id': validation_id,
            'document_id': document_id,
            'client_id': client_id,
            'validator_id': validator_id,
            'extracted_data': extracted_data,
            'status': 'pending',
            'priority': self._calculate_priority(client_id),
            'created_date': datetime.now().isoformat(),
            'validation_notes': None,
            'action': None
        }
        
        self.validations[validation_id] = validation_data
        
        # Añadir a validaciones pendientes del cliente
        if client_id not in self.pending_validations:
            self.pending_validations[client_id] = []
        self.pending_validations[client_id].append(validation_id)
        
        return validation_data
    
    def _find_validator_for_client(self, client_id: str) -> Optional[str]:
        """Encontrar asesor asignado a cliente"""
        for validator_id, validator in self.validators.items():
            if client_id in validator['assigned_clients']:
                return validator_id
        return None
    
    def _calculate_priority(self, client_id: str) -> str:
        """Calcular prioridad de validación"""
        # Lógica simple de priorización
        # En producción, esto podría ser más complejo basado en plan, historial, etc.
        pending_count = len(self.pending_validations.get(client_id, []))
        
        if pending_count > 10:
            return 'high'
        elif pending_count > 5:
            return 'medium'
        else:
            return 'low'
    
    def get_validator_pending_validations(self, validator_id: str) -> Dict:
        """
        Obtener validaciones pendientes de un asesor
        
        Args:
            validator_id: ID del asesor
            
        Returns:
            Diccionario con validaciones pendientes
        """
        if validator_id not in self.validators:
            return {'error': 'Asesor no encontrado'}
        
        validator = self.validators[validator_id]
        pending_validations = []
        
        for validation_id, validation in self.validations.items():
            if (validation['validator_id'] == validator_id and 
                validation['status'] == 'pending'):
                pending_validations.append(validation)
        
        # Ordenar por prioridad
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        pending_validations.sort(
            key=lambda x: priority_order.get(x['priority'], 3)
        )
        
        return {
            'validator_id': validator_id,
            'validator_name': validator['name'],
            'pending_count': len(pending_validations),
            'validations': pending_validations
        }
    
    def validate_transaction(self, validation_id: str, validator_id: str, 
                           action: str, notes: str = None) -> Dict:
        """
        Validar transacción (aprobar, rechazar, observar)
        
        Args:
            validation_id: ID de la validación
            validator_id: ID del asesor
            action: Acción (approve, reject, observe)
            notes: Notas de la validación
            
        Returns:
            Diccionario con resultado de la validación
        """
        if validation_id not in self.validations:
            return {'success': False, 'error': 'Validación no encontrada'}
        
        validation = self.validations[validation_id]
        
        # Verificar que el asesor es el asignado
        if validation['validator_id'] != validator_id:
            return {'success': False, 'error': 'Asesor no autorizado para esta validación'}
        
        # Verificar que la validación está pendiente
        if validation['status'] != 'pending':
            return {'success': False, 'error': 'Validación ya procesada'}
        
        # Actualizar validación
        validation['status'] = 'validated'
        validation['action'] = action
        validation['validation_notes'] = notes
        validation['validation_date'] = datetime.now().isoformat()
        
        # Remover de validaciones pendientes del cliente
        client_id = validation['client_id']
        if client_id in self.pending_validations:
            if validation_id in self.pending_validations[client_id]:
                self.pending_validations[client_id].remove(validation_id)
        
        return {
            'success': True,
            'validation_id': validation_id,
            'action': action,
            'validation_date': validation['validation_date']
        }
    
    def get_validation_history(self, client_id: str) -> Dict:
        """
        Obtener historial de validaciones de un cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con historial de validaciones
        """
        client_validations = []
        
        for validation_id, validation in self.validations.items():
            if validation['client_id'] == client_id:
                client_validations.append(validation)
        
        # Ordenar por fecha de creación
        client_validations.sort(
            key=lambda x: x['created_date'],
            reverse=True
        )
        
        return {
            'client_id': client_id,
            'total_validations': len(client_validations),
            'pending_count': sum(1 for v in client_validations if v['status'] == 'pending'),
            'validated_count': sum(1 for v in client_validations if v['status'] == 'validated'),
            'validations': client_validations
        }
    
    def get_validator_stats(self, validator_id: str) -> Dict:
        """
        Obtener estadísticas de un asesor
        
        Args:
            validator_id: ID del asesor
            
        Returns:
            Diccionario con estadísticas del asesor
        """
        if validator_id not in self.validators:
            return {'error': 'Asesor no encontrado'}
        
        validator = self.validators[validator_id]
        
        # Calcular estadísticas
        validator_validations = [
            v for v in self.validations.values()
            if v['validator_id'] == validator_id
        ]
        
        total_validations = len(validator_validations)
        approved = sum(1 for v in validator_validations if v['action'] == 'approve')
        rejected = sum(1 for v in validator_validations if v['action'] == 'reject')
        observed = sum(1 for v in validator_validations if v['action'] == 'observe')
        
        return {
            'validator_id': validator_id,
            'validator_name': validator['name'],
            'assigned_clients': len(validator['assigned_clients']),
            'total_validations': total_validations,
            'approved': approved,
            'rejected': rejected,
            'observed': observed,
            'approval_rate': approved / total_validations if total_validations > 0 else 0.0
        }


class ValidationQueue:
    """Cola de validaciones para (π)NAD"""
    
    def __init__(self):
        """Inicializar cola de validaciones"""
        self.queue = {}
        self.priority_levels = {'high': 0, 'medium': 1, 'low': 2}
    
    def add_to_queue(self, validation_id: str, priority: str = 'medium'):
        """
        Añadir validación a la cola
        
        Args:
            validation_id: ID de la validación
            priority: Prioridad (high, medium, low)
        """
        self.queue[validation_id] = {
            'validation_id': validation_id,
            'priority': priority,
            'added_date': datetime.now().isoformat()
        }
    
    def get_next_validation(self) -> Optional[Dict]:
        """
        Obtener siguiente validación de la cola (prioridad alta primero)
        
        Returns:
            Diccionario con información de la validación o None
        """
        if not self.queue:
            return None
        
        # Ordenar por prioridad
        sorted_validations = sorted(
            self.queue.values(),
            key=lambda x: (self.priority_levels.get(x['priority'], 3), x['added_date'])
        )
        
        next_validation = sorted_validations[0]
        validation_id = next_validation['validation_id']
        
        # Remover de la cola
        del self.queue[validation_id]
        
        return next_validation
    
    def get_queue_size(self) -> int:
        """Obtener tamaño de la cola"""
        return len(self.queue)
    
    def get_queue_by_priority(self) -> Dict:
        """Obtener cola agrupada por prioridad"""
        queue_by_priority = {'high': [], 'medium': [], 'low': []}
        
        for validation in self.queue.values():
            priority = validation['priority']
            if priority in queue_by_priority:
                queue_by_priority[priority].append(validation)
        
        return queue_by_priority


class ValidationNotifier:
    """Sistema de notificaciones de validación para (π)NAD"""
    
    def __init__(self):
        """Inicializar sistema de notificaciones"""
        self.notifications = {}
    
    def send_validation_notification(self, client_id: str, validation_id: str, 
                                    status: str, message: str) -> Dict:
        """
        Enviar notificación de validación al cliente
        
        Args:
            client_id: ID del cliente
            validation_id: ID de la validación
            status: Estado de la validación
            message: Mensaje de la notificación
            
        Returns:
            Diccionario con resultado de la notificación
        """
        notification_id = str(uuid.uuid4())
        
        notification = {
            'notification_id': notification_id,
            'client_id': client_id,
            'validation_id': validation_id,
            'status': status,
            'message': message,
            'sent_date': datetime.now().isoformat(),
            'read': False
        }
        
        self.notifications[notification_id] = notification
        
        # Aquí se implementaría el envío real (email, SMS, etc.)
        # Por ahora, solo guardamos la notificación
        
        return notification
    
    def get_client_notifications(self, client_id: str) -> List[Dict]:
        """
        Obtener notificaciones de un cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Lista de notificaciones
        """
        return [
            n for n in self.notifications.values()
            if n['client_id'] == client_id
        ]
    
    def mark_notification_as_read(self, notification_id: str) -> Dict:
        """
        Marcar notificación como leída
        
        Args:
            notification_id: ID de la notificación
            
        Returns:
            Diccionario con resultado de la operación
        """
        if notification_id in self.notifications:
            self.notifications[notification_id]['read'] = True
            return {'success': True}
        else:
            return {'success': False, 'error': 'Notificación no encontrada'}
