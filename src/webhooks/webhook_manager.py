"""
Sistema de webhooks para (π)NAD
"""

import hmac
import hashlib
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.exceptions import WebhookException


class WebhookManager:
    """Gestor de webhooks para (π)NAD"""
    
    def __init__(self, secret_key: str = None):
        """
        Inicializar gestor de webhooks
        
        Args:
            secret_key: Clave secreta para firmar webhooks
        """
        self.secret_key = secret_key or 'default_webhook_secret'
        self.logger = get_logger('webhook_manager')
        self.webhooks = {}  # {webhook_id: webhook_info}
    
    def register_webhook(self, webhook_id: str, url: str, events: List[str], 
                        secret: str = None) -> Dict:
        """
        Registrar nuevo webhook
        
        Args:
            webhook_id: ID del webhook
            url: URL del webhook
            events: Lista de eventos a escuchar
            secret: Secreto para verificar firma (opcional)
            
        Returns:
            Información del webhook registrado
        """
        webhook_info = {
            'webhook_id': webhook_id,
            'url': url,
            'events': events,
            'secret': secret or self.secret_key,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_triggered': None,
            'trigger_count': 0,
            'error_count': 0
        }
        
        self.webhooks[webhook_id] = webhook_info
        self.logger.info(f"Webhook registrado: {webhook_id}")
        
        return webhook_info
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Eliminar webhook
        
        Args:
            webhook_id: ID del webhook
            
        Returns:
            True si exitoso, False si falló
        """
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            self.logger.info(f"Webhook eliminado: {webhook_id}")
            return True
        return False
    
    def get_webhook(self, webhook_id: str) -> Optional[Dict]:
        """
        Obtener información de webhook
        
        Args:
            webhook_id: ID del webhook
            
        Returns:
            Información del webhook o None
        """
        return self.webhooks.get(webhook_id)
    
    def trigger_webhook(self, event: str, data: Dict, webhook_id: str = None) -> Dict:
        """
        Disparar webhook para un evento
        
        Args:
            event: Tipo de evento
            data: Datos del evento
            webhook_id: ID específico de webhook (opcional)
            
        Returns:
            Resultado del disparo
        """
        results = []
        
        # Determinar qué webhooks disparar
        if webhook_id:
            webhooks_to_trigger = [self.webhooks.get(webhook_id)] if webhook_id in self.webhooks else []
        else:
            webhooks_to_trigger = [
                webhook for webhook in self.webhooks.values()
                if webhook['status'] == 'active' and event in webhook['events']
            ]
        
        for webhook in webhooks_to_trigger:
            if not webhook:
                continue
            
            try:
                result = self._send_webhook(webhook, event, data)
                results.append(result)
                
                # Actualizar estadísticas
                webhook['last_triggered'] = datetime.now().isoformat()
                webhook['trigger_count'] += 1
                
            except Exception as e:
                self.logger.error(f"Error disparando webhook {webhook['webhook_id']}: {e}")
                webhook['error_count'] += 1
                results.append({
                    'webhook_id': webhook['webhook_id'],
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'event': event,
            'triggered_count': len(results),
            'results': results
        }
    
    def _send_webhook(self, webhook: Dict, event: str, data: Dict) -> Dict:
        """
        Enviar webhook a URL
        
        Args:
            webhook: Información del webhook
            event: Tipo de evento
            data: Datos del evento
            
        Returns:
            Resultado del envío
        """
        # Preparar payload
        payload = {
            'event': event,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Firmar payload
        signature = self._sign_payload(payload, webhook['secret'])
        
        # Enviar request
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-ID': webhook['webhook_id'],
            'X-Event-Type': event
        }
        
        response = requests.post(
            webhook['url'],
            json=payload,
            headers=headers,
            timeout=10
        )
        
        return {
            'webhook_id': webhook['webhook_id'],
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response': response.text if response.text else None
        }
    
    def _sign_payload(self, payload: Dict, secret: str) -> str:
        """
        Firmar payload con HMAC
        
        Args:
            payload: Payload a firmar
            secret: Secreto para firmar
            
        Returns:
            Firma HMAC
        """
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """
        Verificar firma de webhook
        
        Args:
            payload: Payload recibido
            signature: Firma recibida
            secret: Secreto para verificar
            
        Returns:
            True si firma válida, False si no
        """
        expected_signature = self._sign_payload(json.loads(payload), secret)
        return hmac.compare_digest(expected_signature, signature)
    
    def get_webhook_stats(self, webhook_id: str = None) -> Dict:
        """
        Obtener estadísticas de webhooks
        
        Args:
            webhook_id: ID específico de webhook (opcional)
            
        Returns:
            Estadísticas de webhooks
        """
        if webhook_id:
            webhook = self.webhooks.get(webhook_id)
            if webhook:
                return {
                    'webhook_id': webhook_id,
                    'trigger_count': webhook['trigger_count'],
                    'error_count': webhook['error_count'],
                    'last_triggered': webhook['last_triggered'],
                    'status': webhook['status']
                }
            else:
                return {'error': 'Webhook no encontrado'}
        else:
            total_triggers = sum(w['trigger_count'] for w in self.webhooks.values())
            total_errors = sum(w['error_count'] for w in self.webhooks.values())
            active_count = sum(1 for w in self.webhooks.values() if w['status'] == 'active')
            
            return {
                'total_webhooks': len(self.webhooks),
                'active_webhooks': active_count,
                'total_triggers': total_triggers,
                'total_errors': total_errors
            }


class WebhookEvents:
    """Eventos de webhook disponibles para (π)NAD"""
    
    # Eventos de documentos
    DOCUMENT_UPLOADED = 'document.uploaded'
    DOCUMENT_PROCESSED = 'document.processed'
    DOCUMENT_VALIDATED = 'document.validated'
    DOCUMENT_ERROR = 'document.error'
    
    # Eventos de transacciones
    TRANSACTION_CREATED = 'transaction.created'
    TRANSACTION_VALIDATED = 'transaction.validated'
    TRANSACTION_REJECTED = 'transaction.rejected'
    
    # Eventos de clientes
    CLIENT_REGISTERED = 'client.registered'
    CLIENT_UPDATED = 'client.updated'
    CLIENT_DELETED = 'client.deleted'
    
    # Eventos de validación
    VALIDATION_REQUESTED = 'validation.requested'
    VALIDATION_COMPLETED = 'validation.completed'
    
    # Eventos de dashboard
    DASHBOARD_GENERATED = 'dashboard.generated'
    DASHBOARD_EXPORTED = 'dashboard.exported'
    
    # Eventos de sistema
    SYSTEM_ERROR = 'system.error'
    SYSTEM_MAINTENANCE = 'system.maintenance'


class WebhookPayloadBuilder:
    """Constructor de payloads para webhooks"""
    
    @staticmethod
    def document_uploaded(document_id: str, client_id: str, file_name: str) -> Dict:
        """Payload para documento subido"""
        return {
            'document_id': document_id,
            'client_id': client_id,
            'file_name': file_name,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def document_processed(document_id: str, client_id: str, success: bool, 
                         ocr_confidence: float = None) -> Dict:
        """Payload para documento procesado"""
        return {
            'document_id': document_id,
            'client_id': client_id,
            'success': success,
            'ocr_confidence': ocr_confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def transaction_created(transaction_id: str, client_id: str, amount: float, 
                          transaction_type: str) -> Dict:
        """Payload para transacción creada"""
        return {
            'transaction_id': transaction_id,
            'client_id': client_id,
            'amount': amount,
            'type': transaction_type,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def validation_completed(validation_id: str, client_id: str, action: str, 
                           validator_id: str) -> Dict:
        """Payload para validación completada"""
        return {
            'validation_id': validation_id,
            'client_id': client_id,
            'action': action,
            'validator_id': validator_id,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def dashboard_generated(client_id: str, period: str) -> Dict:
        """Payload para dashboard generado"""
        return {
            'client_id': client_id,
            'period': period,
            'timestamp': datetime.now().isoformat()
        }
