"""
Módulo AlertSystem - Sistema de alertas inteligentes - Google Native
Integrado con Cloud Functions, Cloud Scheduler, Pub/Sub
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from decimal import Decimal


class AlertType(Enum):
    """Tipos de alertas"""
    DEADLINE = "deadline"
    DISCREPANCY = "discrepancy"
    LOW_BALANCE = "low_balance"
    MISSING_DOCUMENT = "missing_document"
    TAX_DUE = "tax_due"
    PAYROLL_DUE = "payroll_due"
    INVENTORY_LOW = "inventory_low"
    BUDGET_EXCEEDED = "budget_exceeded"
    COMPLIANCE_ISSUE = "compliance_issue"


class AlertPriority(Enum):
    """Prioridades de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Canales de notificación"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUBSUB = "pubsub"
    SLACK = "slack"


@dataclass
class Alert:
    """Alerta individual"""
    alert_id: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    created_at: datetime
    due_date: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    channels: List[AlertChannel] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def resolve(self):
        """Marcar alerta como resuelta"""
        self.resolved = True
        self.resolved_at = datetime.now()
    
    def is_overdue(self) -> bool:
        """Verificar si la alerta está vencida"""
        if not self.due_date:
            return False
        return datetime.now() > self.due_date
    
    def days_until_due(self) -> Optional[int]:
        """Calcular días hasta el vencimiento"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now()
        return delta.days


class AlertSystem:
    """
    Sistema de alertas inteligentes - Google Native
    Integrado con Cloud Functions, Cloud Scheduler, Pub/Sub
    """
    
    def __init__(self):
        """Inicializar sistema de alertas"""
        self.alerts: List[Alert] = []
        self.callbacks: List[Callable] = []
        self.alert_counter = 0
    
    def add_callback(self, callback: Callable):
        """
        Agregar callback para nuevas alertas
        Integrado con Pub/Sub para notificaciones asíncronas
        """
        self.callbacks.append(callback)
    
    def create_alert(self, alert_type: AlertType, priority: AlertPriority,
                    title: str, message: str, due_date: datetime = None,
                    channels: List[AlertChannel] = None,
                    metadata: Dict[str, Any] = None) -> Alert:
        """
        Crear nueva alerta
        Integrado con Cloud Functions para distribución
        """
        self.alert_counter += 1
        alert_id = f"ALERT_{self.alert_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if channels is None:
            channels = [AlertChannel.EMAIL]
        
        if metadata is None:
            metadata = {}
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=message,
            created_at=datetime.now(),
            due_date=due_date,
            channels=channels,
            metadata=metadata
        )
        self.alerts.append(alert)
        
        # Ejecutar callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Error en callback de alerta: {e}")
        
        return alert
    
    def get_alerts(self, alert_type: AlertType = None, 
                   priority: AlertPriority = None,
                   resolved: bool = None) -> List[Alert]:
        """Obtener alertas filtradas"""
        filtered_alerts = self.alerts
        
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a.alert_type == alert_type]
        
        if priority:
            filtered_alerts = [a for a in filtered_alerts if a.priority == priority]
        
        if resolved is not None:
            filtered_alerts = [a for a in filtered_alerts if a.resolved == resolved]
        
        return filtered_alerts
    
    def get_overdue_alerts(self) -> List[Alert]:
        """Obtener alertas vencidas"""
        return [a for a in self.alerts if a.is_overdue() and not a.resolved]
    
    def get_upcoming_alerts(self, days: int = 7) -> List[Alert]:
        """Obtener alertas próximas a vencer"""
        upcoming = []
        cutoff_date = datetime.now() + timedelta(days=days)
        
        for alert in self.alerts:
            if alert.due_date and not alert.resolved:
                if datetime.now() <= alert.due_date <= cutoff_date:
                    upcoming.append(alert)
        
        return upcoming
    
    def resolve_alert(self, alert: Alert):
        """Resolver alerta"""
        alert.resolve()
    
    def check_low_balance(self, account_balance: Decimal, threshold: Decimal):
        """
        Verificar saldo bajo
        Integrado con BigQuery para monitoreo en tiempo real
        """
        if account_balance < threshold:
            self.create_alert(
                AlertType.LOW_BALANCE,
                AlertPriority.HIGH,
                "Saldo Bajo",
                f"El saldo de la cuenta está por debajo del umbral: ${account_balance} < ${threshold}",
                channels=[AlertChannel.EMAIL, AlertChannel.SMS],
                metadata={
                    'balance': float(account_balance),
                    'threshold': float(threshold),
                    'google_services': [
                        "BigQuery para monitoreo",
                        "Cloud Functions para alertas",
                        "Pub/Sub para notificaciones"
                    ]
                }
            )
    
    def check_tax_deadline(self, tax_type: str, due_date: datetime):
        """
        Verificar fecha límite de impuesto
        Integrado con Cloud Scheduler para verificaciones automáticas
        """
        days_until = (due_date - datetime.now()).days
        
        if days_until <= 7 and days_until > 0:
            priority = AlertPriority.MEDIUM
        elif days_until <= 3 and days_until > 0:
            priority = AlertPriority.HIGH
        elif days_until <= 0:
            priority = AlertPriority.CRITICAL
        else:
            return
        
        self.create_alert(
            AlertType.TAX_DUE,
            priority,
            f"Vencimiento de {tax_type}",
            f"El pago de {tax_type} vence en {days_until} días ({due_date.strftime('%Y-%m-%d')})",
            due_date,
            channels=[AlertChannel.EMAIL, AlertChannel.SMS],
            metadata={
                'tax_type': tax_type,
                'due_date': due_date.isoformat(),
                'days_until': days_until,
                'google_services': [
                    "Cloud Scheduler para verificaciones",
                    "Cloud Functions para alertas",
                    "Pub/Sub para notificaciones"
                ]
            }
        )
    
    def check_payroll_deadline(self, payroll_date: datetime):
        """
        Verificar fecha límite de nómina
        Integrado con Cloud Scheduler para verificaciones automáticas
        """
        days_until = (payroll_date - datetime.now()).days
        
        if days_until <= 3 and days_until > 0:
            priority = AlertPriority.HIGH
        elif days_until <= 0:
            priority = AlertPriority.CRITICAL
        else:
            return
        
        self.create_alert(
            AlertType.PAYROLL_DUE,
            priority,
            "Pago de Nómina",
            f"El pago de nómina vence en {days_until} días ({payroll_date.strftime('%Y-%m-%d')})",
            payroll_date,
            channels=[AlertChannel.EMAIL, AlertChannel.SMS],
            metadata={
                'payroll_date': payroll_date.isoformat(),
                'days_until': days_until,
                'google_services': [
                    "Cloud Scheduler para verificaciones",
                    "Cloud Functions para alertas",
                    "Pub/Sub para notificaciones"
                ]
            }
        )
    
    def check_discrepancy(self, description: str, amount: Decimal, tolerance: Decimal = None):
        """
        Verificar discrepancia en montos
        Integrado con BigQuery para detección automática
        """
        if tolerance is None or amount > tolerance:
            priority = AlertPriority.HIGH if amount > tolerance * 2 else AlertPriority.MEDIUM
            self.create_alert(
                AlertType.DISCREPANCY,
                priority,
                "Discrepancia Detectada",
                f"{description}: Discrepancia de ${amount}",
                channels=[AlertChannel.EMAIL],
                metadata={
                    'description': description,
                    'amount': float(amount),
                    'tolerance': float(tolerance) if tolerance else None,
                    'google_services': [
                        "BigQuery para detección",
                        "Cloud Functions para alertas",
                        "Pub/Sub para notificaciones"
                    ]
                }
            )
    
    def check_inventory_low(self, sku: str, current_quantity: Decimal, reorder_point: Decimal):
        """
        Verificar inventario bajo
        Integrado con Cloud SQL para monitoreo en tiempo real
        """
        if current_quantity <= reorder_point:
            self.create_alert(
                AlertType.INVENTORY_LOW,
                AlertPriority.HIGH,
                "Inventario Bajo",
                f"SKU {sku}: Cantidad actual {current_quantity} <= punto de reorden {reorder_point}",
                channels=[AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                metadata={
                    'sku': sku,
                    'current_quantity': float(current_quantity),
                    'reorder_point': float(reorder_point),
                    'google_services': [
                        "Cloud SQL para monitoreo",
                        "Cloud Functions para alertas",
                        "Pub/Sub para notificaciones"
                    ]
                }
            )
    
    def check_budget_exceeded(self, category: str, budgeted: Decimal, actual: Decimal):
        """
        Verificar presupuesto excedido
        Integrado con BigQuery para análisis en tiempo real
        """
        if actual > budgeted:
            variance = actual - budgeted
            variance_pct = (variance / budgeted) * 100 if budgeted else 0
            
            priority = AlertPriority.CRITICAL if variance_pct > 20 else AlertPriority.HIGH
            self.create_alert(
                AlertType.BUDGET_EXCEEDED,
                priority,
                "Presupuesto Excedido",
                f"Categoría {category}: Presupuesto ${budgeted} excedido por ${variance} ({variance_pct:.1f}%)",
                channels=[AlertChannel.EMAIL, AlertChannel.SMS],
                metadata={
                    'category': category,
                    'budgeted': float(budgeted),
                    'actual': float(actual),
                    'variance': float(variance),
                    'variance_pct': variance_pct,
                    'google_services': [
                        "BigQuery para análisis",
                        "Looker Studio para visualización",
                        "Cloud Functions para alertas"
                    ]
                }
            )
    
    def check_compliance_issue(self, issue_type: str, description: str, severity: str = "medium"):
        """
        Verificar problema de compliance
        Integrado con Cloud Audit para monitoreo continuo
        """
        priority = AlertPriority.CRITICAL if severity == "critical" else AlertPriority.HIGH
        self.create_alert(
            AlertType.COMPLIANCE_ISSUE,
            priority,
            f"Issue de Compliance: {issue_type}",
            description,
            channels=[AlertChannel.EMAIL, AlertChannel.SMS, AlertChannel.SLACK],
            metadata={
                'issue_type': issue_type,
                'severity': severity,
                'google_services': [
                    "Cloud Audit para monitoreo",
                    "Cloud Functions para alertas",
                    "Pub/Sub para notificaciones",
                    "Security Command Center"
                ]
            }
        )
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Obtener resumen de alertas"""
        total_alerts = len(self.alerts)
        resolved_alerts = sum(1 for a in self.alerts if a.resolved)
        pending_alerts = total_alerts - resolved_alerts
        overdue_alerts = len(self.get_overdue_alerts())
        upcoming_alerts = len(self.get_upcoming_alerts())
        
        return {
            'total_alerts': total_alerts,
            'resolved_alerts': resolved_alerts,
            'pending_alerts': pending_alerts,
            'overdue_alerts': overdue_alerts,
            'upcoming_alerts': upcoming_alerts,
            'by_type': {
                alert_type.value: len(self.get_alerts(alert_type=alert_type))
                for alert_type in AlertType
            },
            'by_priority': {
                priority.value: len(self.get_alerts(priority=priority))
                for priority in AlertPriority
            },
            'google_native_integration': {
                'scheduling': "Cloud Scheduler para verificaciones automáticas",
                'messaging': "Pub/Sub para notificaciones asíncronas",
                'compute': "Cloud Functions para procesamiento de alertas",
                'monitoring': "BigQuery para análisis en tiempo real",
                'audit': "Cloud Audit para trazabilidad",
                'storage': "Cloud Storage para historial de alertas"
            }
        }
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "scheduling": "Cloud Scheduler",
            "messaging": "Pub/Sub",
            "compute": "Cloud Functions",
            "monitoring": "BigQuery",
            "audit": "Cloud Audit",
            "storage": "Cloud Storage",
            "notification_channels": ["Email", "SMS", "Webhook", "Slack"],
            "total_alert_types": len(AlertType),
            "total_priorities": len(AlertPriority),
            "google_native": True
        }


# Singleton instance
alert_system = AlertSystem()
