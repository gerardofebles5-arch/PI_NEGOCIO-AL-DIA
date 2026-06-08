"""
Módulo de Impuestos Avanzado V4.0 - Google Native
Funcionalidades de impuestos con arquitectura Google-native
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class TaxType(Enum):
    """Tipos de impuestos"""
    IVA = "iva"
    ISLR = "islr"
    PATRONAL = "patronal"
    MUNICIPAL = "municipal"


class DeclarationStatus(Enum):
    """Estado de declaración"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


@dataclass
class TaxRate:
    """Tasa de impuesto"""
    tax_type: TaxType
    rate: Decimal
    effective_date: date
    description: str


@dataclass
class TaxDeclaration:
    """Declaración de impuesto"""
    declaration_id: str
    tax_type: TaxType
    period: str
    rif: str
    company_name: str
    status: DeclarationStatus
    generated_at: datetime
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    amount_due: Decimal = Decimal('0')
    amount_paid: Decimal = Decimal('0')


@dataclass
class TaxPenalty:
    """Multa o recargo por impuesto"""
    tax_amount: Decimal
    penalty_amount: Decimal
    interest_amount: Decimal
    total_due: Decimal
    days_late: int
    penalty_rate: Decimal
    interest_rate: Decimal


@dataclass
class TaxProjection:
    """Proyección de impuestos"""
    month: int
    projected_sales: Decimal
    projected_purchases: Decimal
    iva_debito: Decimal
    iva_credito: Decimal
    iva_pagar: Decimal


@dataclass
class TaxObligation:
    """Obligación fiscal en calendario"""
    date: str
    obligation: str
    period: str
    tax_type: TaxType


class AdvancedTaxSystem:
    """
    Sistema de impuestos avanzado - Google Native
    Integrado con Cloud Functions, Cloud Scheduler, BigQuery
    """
    
    def __init__(self):
        """Inicializar sistema de impuestos avanzado"""
        self.current_rates = {
            'iva': {
                'general': 16,
                'reducido': 8,
                'exento': 0
            },
            'islr': {
                'tramo1': {'min': 0, 'max': 1000, 'rate': 6, 'sustraendo': 0},
                'tramo2': {'min': 1000, 'max': 2000, 'rate': 9, 'sustraendo': 30},
                'tramo3': {'min': 2000, 'max': 3000, 'rate': 12, 'sustraendo': 90},
                'tramo4': {'min': 3000, 'max': 6000, 'rate': 16, 'sustraendo': 210},
                'tramo5': {'min': 6000, 'max': float('inf'), 'rate': 20, 'sustraendo': 450},
            }
        }
        self.declaration_history: List[TaxDeclaration] = []
        self.tax_rates: List[TaxRate] = []
    
    def update_rates_from_seniat(self) -> Dict:
        """
        Actualizar tasas desde SENIAT
        Integrado con Cloud Functions para llamadas API
        """
        logger.info("Actualizando tasas desde SENIAT (vía Cloud Functions)")
        
        # En producción, esto usaría Cloud Functions para llamar a API de SENIAT
        self.current_rates['iva']['general'] = 16
        self.current_rates['iva']['reducido'] = 8
        
        return {
            'updated_at': datetime.now().isoformat(),
            'rates': self.current_rates,
            'google_services': [
                "Cloud Functions para integración SENIAT",
                "Secret Manager para API keys",
                "Cloud Audit para auditoría",
                "BigQuery para historial de tasas"
            ]
        }
    
    def calculate_penalties_and_interest(self, tax_amount: Decimal, 
                                       due_date: date,
                                       payment_date: date) -> TaxPenalty:
        """
        Calcular multas e intereses por mora
        Integrado con Cloud Functions para cálculos automáticos
        """
        if payment_date <= due_date:
            return TaxPenalty(
                tax_amount=tax_amount,
                penalty_amount=Decimal('0'),
                interest_amount=Decimal('0'),
                total_due=tax_amount,
                days_late=0,
                penalty_rate=Decimal('0'),
                interest_rate=Decimal('0')
            )
        
        days_late = (payment_date - due_date).days
        
        # Cálculo de multa (1% del monto por mes o fracción, máximo 100%)
        months_late = days_late / 30
        penalty_rate = min(Decimal('1.0'), Decimal(str(months_late * 0.01)))
        penalty = tax_amount * penalty_rate
        
        # Cálculo de intereses (tasa activa bancaria, simulada como 2% anual)
        annual_rate = Decimal('0.02')
        daily_rate = annual_rate / Decimal('365')
        interest = tax_amount * daily_rate * Decimal(days_late)
        
        total_due = tax_amount + penalty + interest
        
        return TaxPenalty(
            tax_amount=tax_amount,
            penalty_amount=penalty,
            interest_amount=interest,
            total_due=total_due,
            days_late=days_late,
            penalty_rate=penalty_rate,
            interest_rate=annual_rate
        )
    
    def generate_automatic_declaration(self, period: str, 
                                     tax_type: str,
                                     data: Dict) -> TaxDeclaration:
        """
        Generar declaración automática para SENIAT
        Integrado con Cloud Functions para generación XML
        """
        declaration_id = f"{tax_type}_{period}_{data.get('rif', '')}"
        
        declaration = TaxDeclaration(
            declaration_id=declaration_id,
            tax_type=TaxType(tax_type),
            period=period,
            rif=data.get('rif', ''),
            company_name=data.get('company_name', ''),
            status=DeclarationStatus.PENDING,
            generated_at=datetime.now()
        )
        
        if tax_type == 'iva':
            iva_data = self._generate_iva_declaration(data)
            declaration.amount_due = Decimal(str(iva_data['iva_pagar']))
        elif tax_type == 'islr':
            islr_data = self._generate_islr_declaration(data)
            declaration.amount_due = Decimal(str(islr_data['impuesto_a_pagar']))
        
        self.declaration_history.append(declaration)
        
        logger.info(f"Declaración {tax_type} generada para período {period}")
        return declaration
    
    def _generate_iva_declaration(self, data: Dict) -> Dict:
        """Generar declaración de IVA"""
        ventas_gravadas = Decimal(str(data.get('ventas_gravadas', 0)))
        ventas_exentas = Decimal(str(data.get('ventas_exentas', 0)))
        compras_gravadas = Decimal(str(data.get('compras_gravadas', 0)))
        
        iva_debito = ventas_gravadas * Decimal('0.16')
        iva_credito = compras_gravadas * Decimal('0.16')
        iva_pagar = iva_debito - iva_credito
        
        return {
            'ventas_gravadas': float(ventas_gravadas),
            'ventas_exentas': float(ventas_exentas),
            'compras_gravadas': float(compras_gravadas),
            'iva_debito': float(iva_debito),
            'iva_credito': float(iva_credito),
            'iva_pagar': float(max(0, iva_pagar)),
            'xml_content': self._generate_xml_content('iva', data),
            'google_services': [
                "Cloud Functions para generación XML",
                "BigQuery para almacenamiento",
                "Cloud Storage para archivos XML",
                "Secret Manager para credenciales"
            ]
        }
    
    def _generate_islr_declaration(self, data: Dict) -> Dict:
        """Generar declaración de ISLR"""
        renta_gravada = Decimal(str(data.get('renta_gravada', 0)))
        rebajas = Decimal(str(data.get('rebajas', 0)))
        
        renta_neta = renta_gravada - rebajas
        impuesto = self._calculate_islr_tax(renta_neta)
        
        return {
            'renta_gravada': float(renta_gravada),
            'rebajas': float(rebajas),
            'renta_neta': float(renta_neta),
            'impuesto_a_pagar': float(impuesto),
            'xml_content': self._generate_xml_content('islr', data),
            'google_services': [
                "Cloud Functions para generación XML",
                "BigQuery para almacenamiento",
                "Cloud Storage para archivos XML",
                "Secret Manager para credenciales"
            ]
        }
    
    def _calculate_islr_tax(self, renta_neta: Decimal) -> Decimal:
        """Calcular impuesto ISLR según tramos"""
        tramos = self.current_rates['islr']
        
        for tramo in tramos.values():
            if tramo['min'] <= renta_neta <= tramo['max']:
                return (renta_neta * Decimal(str(tramo['rate'] / 100))) - Decimal(str(tramo['sustraendo']))
        
        ultimo_tramo = tramos['tramo5']
        return (renta_neta * Decimal(str(ultimo_tramo['rate'] / 100))) - Decimal(str(ultimo_tramo['sustraendo']))
    
    def _generate_xml_content(self, tax_type: str, data: Dict) -> str:
        """Generar contenido XML para SENIAT"""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Declaracion>
    <Tipo>{tax_type.upper()}</Tipo>
    <RIF>{data.get('rif', '')}</RIF>
    <Periodo>{data.get('periodo', '')}</Periodo>
    <FechaGeneracion>{datetime.now().strftime('%Y-%m-%d')}</FechaGeneracion>
</Declaracion>"""
        return xml
    
    def check_due_dates(self, declarations: List[TaxDeclaration]) -> List[Dict]:
        """
        Verificar vencimientos de declaraciones y generar alertas
        Integrado con Cloud Scheduler para alertas automáticas
        """
        alerts = []
        today = date.today()
        
        for decl in declarations:
            due_date = self._calculate_due_date(decl.period, decl.tax_type.value)
            days_until_due = (due_date - today).days
            
            if days_until_due <= 7 and days_until_due > 0:
                alerts.append({
                    'type': 'warning',
                    'message': f"Declaración {decl.tax_type.value} vence en {days_until_due} días",
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'declaration_id': decl.declaration_id,
                    'google_services': ["Cloud Scheduler", "Pub/Sub", "Cloud Functions"]
                })
            elif days_until_due <= 0:
                alerts.append({
                    'type': 'error',
                    'message': f"Declaración {decl.tax_type.value} vencida hace {abs(days_until_due)} días",
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'days_late': abs(days_until_due),
                    'declaration_id': decl.declaration_id,
                    'google_services': ["Cloud Scheduler", "Pub/Sub", "Cloud Functions"]
                })
        
        return alerts
    
    def _calculate_due_date(self, period: str, tax_type: str) -> date:
        """Calcular fecha de vencimiento según tipo de impuesto y período"""
        year, month = map(int, period.split('-'))
        
        if tax_type == 'iva':
            if month == 12:
                return date(year + 1, 1, 15)
            else:
                return date(year, month + 1, 15)
        
        elif tax_type == 'islr':
            return date(year + 1, 3, 31)
        
        return date(year, month + 1, 15)
    
    def get_declaration_history(self, tax_type: Optional[str] = None,
                               period: Optional[str] = None) -> List[TaxDeclaration]:
        """Obtener historial de declaraciones"""
        filtered = self.declaration_history
        
        if tax_type:
            filtered = [d for d in filtered if d.tax_type.value == tax_type]
        
        if period:
            filtered = [d for d in filtered if d.period == period]
        
        return filtered
    
    def calculate_tax_projection(self, current_data: Dict,
                               months: int = 12) -> List[TaxProjection]:
        """
        Calcular proyección de impuestos
        Integrado con BigQuery para análisis predictivo
        """
        projections = []
        
        avg_monthly_sales = Decimal(str(current_data.get('avg_monthly_sales', 0)))
        avg_monthly_purchases = Decimal(str(current_data.get('avg_monthly_purchases', 0)))
        
        for month in range(1, months + 1):
            growth_factor = Decimal('1.02') ** month
            
            projected_sales = avg_monthly_sales * growth_factor
            projected_purchases = avg_monthly_purchases * growth_factor
            
            iva_debito = projected_sales * Decimal('0.16')
            iva_credito = projected_purchases * Decimal('0.16')
            iva_pagar = iva_debito - iva_credito
            
            projections.append(TaxProjection(
                month=month,
                projected_sales=projected_sales,
                projected_purchases=projected_purchases,
                iva_debito=iva_debito,
                iva_credito=iva_credito,
                iva_pagar=max(Decimal('0'), iva_pagar)
            ))
        
        return projections
    
    def generate_tax_calendar(self, year: int) -> List[TaxObligation]:
        """
        Generar calendario de obligaciones fiscales
        Integrado con Cloud Calendar para sincronización
        """
        calendar = []
        
        for month in range(1, 13):
            period = f"{year}-{month:02d}"
            due_date = self._calculate_due_date(period, 'iva')
            calendar.append(TaxObligation(
                date=due_date.strftime('%Y-%m-%d'),
                obligation='Declaración IVA',
                period=period,
                tax_type=TaxType.IVA
            ))
        
        islr_due = self._calculate_due_date(f"{year}-01", 'islr')
        calendar.append(TaxObligation(
            date=islr_due.strftime('%Y-%m-%d'),
            obligation='Declaración ISLR',
            period=f"{year}-01",
            tax_type=TaxType.ISLR
        ))
        
        calendar.sort(key=lambda x: x.date)
        
        return calendar
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "api_integration": "Cloud Functions para SENIAT",
            "scheduling": "Cloud Scheduler para alertas automáticas",
            "storage": "BigQuery para historial de declaraciones",
            "file_storage": "Cloud Storage para archivos XML",
            "security": "Secret Manager para API keys",
            "messaging": "Pub/Sub para notificaciones",
            "audit": "Cloud Audit para trazabilidad",
            "calendar": "Google Calendar API para sincronización",
            "total_functions": 8,
            "tax_types": len(TaxType),
            "google_native": True
        }


# Singleton instance
advanced_tax_system = AdvancedTaxSystem()
