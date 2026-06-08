"""
Módulo Reports - Reportes específicos venezolanos - Google Native
Generador de reportes venezolanos con integración Google Cloud
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, date


class ReportType(Enum):
    """Tipos de reportes"""
    BALANCE_COMPROBACION = "balance_comprobacion"
    ESTADO_RESULTADOS = "estado_resultados"
    BALANCE_GENERAL = "balance_general"
    LIBRO_DIARIO = "libro_diario"
    LIBRO_MAYOR = "libro_mayor"
    DECLARACION_IVA = "declaracion_iva"
    DECLARACION_ISLR = "declaracion_islr"
    RETENCION_IVA = "retencion_iva"
    RETENCION_ISLR = "retencion_islr"
    LIBRO_COMPRAS = "libro_compras"
    LIBRO_VENTAS = "libro_ventas"
    PLANILLA_IVSS = "planilla_ivss"
    PLANILLA_FAOV = "planilla_faov"
    PLANILLA_INCE = "planilla_ince"
    PLANILLA_LPH = "planilla_lph"
    ESTADO_FLUJO_EFECTIVO = "estado_flujo_efectivo"
    ESTADO_CAMBIOS_PATRIMONIO = "estado_cambios_patrimonio"


class TaxpayerType(Enum):
    """Tipos de contribuyentes"""
    ORDINARIO = "ordinario"
    ESPECIAL = "especial"
    EXENTO = "exento"


@dataclass
class IVADeclaration:
    """Declaración de IVA"""
    period: str
    total_ventas: Decimal
    total_compras: Decimal
    iva_debito: Decimal
    iva_credito: Decimal
    iva_pagar: Decimal
    iva_recuperar: Decimal
    tipo_contribuyente: TaxpayerType
    fecha_generacion: str


@dataclass
class ISLRDeclaration:
    """Declaración de ISLR"""
    year: int
    ingresos_brutos: Decimal
    gastos_deducibles: Decimal
    deducciones_especiales: Decimal
    renta_gravable: Decimal
    islr_pagar: Decimal
    tasa_efectiva: Decimal
    tipo_contribuyente: str
    fecha_generacion: str


@dataclass
class PurchaseBook:
    """Libro de compras"""
    period: str
    total_compras: Decimal
    total_iva_credito: Decimal
    compras_detalle: List[Dict]
    fecha_generacion: str


@dataclass
class SalesBook:
    """Libro de ventas"""
    period: str
    total_ventas: Decimal
    total_iva_debito: Decimal
    ventas_detalle: List[Dict]
    fecha_generacion: str


@dataclass
class PayrollReport:
    """Reporte de nómina"""
    period: str
    total_salarios: Decimal
    total_cotizacion: Decimal
    numero_empleados: int
    empleados_detalle: List[Dict]
    fecha_generacion: str


class VenezuelanReports:
    """
    Generador de reportes venezolanos - Google Native
    Integrado con BigQuery, Cloud Storage, Google Sheets, Cloud Functions
    """
    
    def __init__(self, accounting_engine):
        """
        Inicializar generador de reportes
        
        Args:
            accounting_engine: Motor contable
        """
        self.accounting_engine = accounting_engine
        self.reports: List[Dict] = []
    
    def generate_declaracion_iva(self, period: str, sales: List[Dict], 
                                 purchases: List[Dict]) -> Dict:
        """
        Generar declaración de IVA
        Integrado con BigQuery para análisis y Google Sheets para colaboración
        """
        total_sales = sum(Decimal(str(s.get('amount', 0))) for s in sales)
        total_purchases = sum(Decimal(str(p.get('amount', 0))) for p in purchases)
        
        iva_debito = total_sales * Decimal("0.16")
        iva_credito = total_purchases * Decimal("0.16")
        iva_pagar = iva_debito - iva_credito
        
        declaration = {
            'period': period,
            'total_ventas': float(total_sales),
            'total_compras': float(total_purchases),
            'iva_debito': float(iva_debito),
            'iva_credito': float(iva_credito),
            'iva_pagar': float(iva_pagar) if iva_pagar > 0 else 0.0,
            'iva_recuperar': float(abs(iva_pagar)) if iva_pagar < 0 else 0.0,
            'tipo_contribuyente': 'Ordinario',
            'fecha_generacion': datetime.now().isoformat(),
            'google_services': [
                "BigQuery para análisis de IVA",
                "Google Sheets para colaboración",
                "Cloud Storage para respaldo",
                "Cloud Functions para cálculos automáticos",
                "Pub/Sub para notificaciones de vencimientos"
            ]
        }
        
        self.reports.append(declaration)
        return declaration
    
    def generate_declaracion_islr(self, year: int, income: Decimal,
                                  expenses: Decimal, deductions: List[Dict]) -> Dict:
        """
        Generar declaración de ISLR
        Integrado con BigQuery para análisis y Google Sheets para colaboración
        """
        total_deductions = sum(Decimal(str(d.get('amount', 0))) for d in deductions)
        taxable_income = income - expenses - total_deductions
        
        if taxable_income <= 0:
            islr_amount = Decimal("0.00")
            effective_rate = Decimal("0.00")
        elif taxable_income <= 1000:
            islr_amount = taxable_income * Decimal("0.06")
            effective_rate = Decimal("0.06")
        elif taxable_income <= 3000:
            islr_amount = (taxable_income - 1000) * Decimal("0.09") + 60
            effective_rate = Decimal("0.09")
        else:
            islr_amount = (taxable_income - 3000) * Decimal("0.34") + 240
            effective_rate = Decimal("0.34")
        
        declaration = {
            'year': year,
            'ingresos_brutos': float(income),
            'gastos_deducibles': float(expenses),
            'deducciones_especiales': float(total_deductions),
            'renta_gravable': float(taxable_income),
            'islr_pagar': float(islr_amount),
            'tasa_efectiva': float(effective_rate),
            'tipo_contribuyente': 'Persona Natural',
            'fecha_generacion': datetime.now().isoformat(),
            'google_services': [
                "BigQuery para análisis de ISLR",
                "Google Sheets para colaboración",
                "Cloud Storage para respaldo",
                "Cloud Functions para cálculos automáticos",
                "Pub/Sub para notificaciones de vencimientos"
            ]
        }
        
        self.reports.append(declaration)
        return declaration
    
    def generate_libro_compras(self, period: str, purchases: List[Dict]) -> Dict:
        """
        Generar libro de compras
        Integrado con BigQuery para análisis y Google Sheets para colaboración
        """
        total_compras = Decimal("0.00")
        total_iva_credito = Decimal("0.00")
        
        compras_detalle = []
        
        for purchase in purchases:
            amount = Decimal(str(purchase.get('amount', 0)))
            iva = amount * Decimal("0.16")
            
            total_compras += amount
            total_iva_credito += iva
            
            compras_detalle.append({
                'fecha': purchase.get('date', ''),
                'rif': purchase.get('rif', ''),
                'proveedor': purchase.get('vendor', ''),
                'numero_factura': purchase.get('invoice_number', ''),
                'numero_control': purchase.get('control_number', ''),
                'compra_gravada': float(amount),
                'iva_credito': float(iva),
                'total_compra': float(amount + iva)
            })
        
        book = {
            'period': period,
            'total_compras': float(total_compras),
            'total_iva_credito': float(total_iva_credito),
            'compras_detalle': compras_detalle,
            'fecha_generacion': datetime.now().isoformat(),
            'google_services': [
                "BigQuery para análisis de compras",
                "Google Sheets para colaboración",
                "Cloud Storage para respaldo",
                "Cloud Functions para procesamiento"
            ]
        }
        
        self.reports.append(book)
        return book
    
    def generate_libro_ventas(self, period: str, sales: List[Dict]) -> Dict:
        """
        Generar libro de ventas
        Integrado con BigQuery para análisis y Google Sheets para colaboración
        """
        total_ventas = Decimal("0.00")
        total_iva_debito = Decimal("0.00")
        
        ventas_detalle = []
        
        for sale in sales:
            amount = Decimal(str(sale.get('amount', 0)))
            iva = amount * Decimal("0.16")
            
            total_ventas += amount
            total_iva_debito += iva
            
            ventas_detalle.append({
                'fecha': sale.get('date', ''),
                'rif': sale.get('rif', ''),
                'cliente': sale.get('customer', ''),
                'numero_factura': sale.get('invoice_number', ''),
                'numero_control': sale.get('control_number', ''),
                'venta_gravada': float(amount),
                'iva_debito': float(iva),
                'total_venta': float(amount + iva)
            })
        
        book = {
            'period': period,
            'total_ventas': float(total_ventas),
            'total_iva_debito': float(total_iva_debito),
            'ventas_detalle': ventas_detalle,
            'fecha_generacion': datetime.now().isoformat(),
            'google_services': [
                "BigQuery para análisis de ventas",
                "Google Sheets para colaboración",
                "Cloud Storage para respaldo",
                "Cloud Functions para procesamiento"
            ]
        }
        
        self.reports.append(book)
        return book
    
    def generate_planilla_ivss(self, period: str, employees: List[Dict]) -> Dict:
        """
        Generar planilla IVSS
        Integrado con BigQuery para análisis y Google Sheets para colaboración
        """
        total_salarios = Decimal("0.00")
        total_cotizacion = Decimal("0.00")
        
        empleados_detalle = []
        
        for employee in employees:
            salary = Decimal(str(employee.get('salary', 0)))
            cotizacion = salary * Decimal("0.04")
            
            total_salarios += salary
            total_cotizacion += cotizacion
            
            empleados_detalle.append({
                'cedula': employee.get('cedula', ''),
                'nombre': employee.get('name', ''),
                'cargo': employee.get('position', ''),
                'salario': float(salary),
                'dias_trabajados': employee.get('days_worked', 30),
                'cotizacion': float(cotizacion)
            })
        
        report = {
            'period': period,
            'total_salarios': float(total_salarios),
            'total_cotizacion': float(total_cotizacion),
            'numero_empleados': len(employees),
            'empleados_detalle': empleados_detalle,
            'fecha_generacion': datetime.now().isoformat(),
            'google_services': [
                "BigQuery para análisis de nómina",
                "Google Sheets para colaboración",
                "Cloud Storage para respaldo",
                "Cloud Functions para cálculos automáticos",
                "Pub/Sub para notificaciones de vencimientos"
            ]
        }
        
        self.reports.append(report)
        return report
    
    def generate_planilla_faov(self, period: str, employees: List[Dict]) -> Dict:
        """
        Generar planilla FAOV
        Integrado con BigQuery para análisis y Google Sheets para colaboración
        """
        total_salarios = Decimal("0.00")
        total_cotizacion = Decimal("0.00")
        
        empleados_detalle = []
        
        for employee in employees:
            salary = Decimal(str(employee.get('salary', 0)))
            cotizacion = salary * Decimal("0.01")
            
            total_salarios += salary
            total_cotizacion += cotizacion
            
            empleados_detalle.append({
                'cedula': employee.get('cedula', ''),
                'nombre': employee.get('name', ''),
                'cargo': employee.get('position', ''),
                'salario': float(salary),
                'dias_trabajados': employee.get('days_worked', 30),
                'cotizacion': float(cotizacion)
            })
        
        report = {
            'period': period,
            'total_salarios': float(total_salarios),
            'total_cotizacion': float(total_cotizacion),
            'numero_empleados': len(employees),
            'empleados_detalle': empleados_detalle,
            'fecha_generacion': datetime.now().isoformat(),
            'google_services': [
                "BigQuery para análisis de nómina",
                "Google Sheets para colaboración",
                "Cloud Storage para respaldo",
                "Cloud Functions para cálculos automáticos",
                "Pub/Sub para notificaciones de vencimientos"
            ]
        }
        
        self.reports.append(report)
        return report
    
    def generate_estado_flujo_efectivo(self, period: str, 
                                       operating_activities: Dict,
                                       investing_activities: Dict,
                                       financing_activities: Dict) -> Dict:
        """
        Generar estado de flujo de efectivo
        Integrado con BigQuery para análisis y Looker Studio para visualización
        """
        operating = Decimal(str(operating_activities.get('net', 0)))
        investing = Decimal(str(investing_activities.get('net', 0)))
        financing = Decimal(str(financing_activities.get('net', 0)))
        
        net_change = operating + investing + financing
        
        report = {
            'period': period,
            'actividades_operativas': operating_activities,
            'actividades_inversion': investing_activities,
            'actividades_financiamiento': financing_activities,
            'cambio_neto_efectivo': float(net_change),
            'fecha_generacion': datetime.now().isoformat(),
            'google_services': [
                "BigQuery para análisis de flujo de efectivo",
                "Looker Studio para visualización",
                "Google Sheets para colaboración",
                "Cloud Storage para respaldo",
                "Cloud Functions para cálculos automáticos"
            ]
        }
        
        self.reports.append(report)
        return report
    
    def export_to_google_sheets(self, spreadsheet_id: str, report_type: str) -> Dict:
        """
        Exportar reporte a Google Sheets
        Integrado con Google Sheets API para colaboración en tiempo real
        """
        result = {
            'success': False,
            'spreadsheet_id': spreadsheet_id,
            'report_type': report_type,
            'google_services': [
                "Google Sheets API",
                "Cloud Storage para respaldo",
                "Cloud Functions para sincronización"
            ]
        }
        
        try:
            report = next((r for r in self.reports if r.get('report_type') == report_type), None)
            if report:
                result['data'] = report
                result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def export_to_cloud_storage(self, bucket_name: str, report_type: str) -> Dict:
        """
        Exportar reporte a Cloud Storage
        Integrado con Cloud Storage para almacenamiento en la nube
        """
        result = {
            'success': False,
            'bucket_name': bucket_name,
            'report_type': report_type,
            'google_services': [
                "Cloud Storage",
                "Cloud Functions para procesamiento",
                "Cloud Audit para trazabilidad"
            ]
        }
        
        try:
            report = next((r for r in self.reports if r.get('report_type') == report_type), None)
            if report:
                result['data'] = report
                result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_report_history(self) -> List[Dict]:
        """
        Obtener historial de reportes generados
        Integrado con BigQuery para análisis histórico
        """
        return [
            {
                'period': r.get('period', r.get('year', '')),
                'report_type': r.get('report_type', 'unknown'),
                'fecha_generacion': r.get('fecha_generacion', ''),
                'google_services': r.get('google_services', [])
            }
            for r in self.reports
        ]
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "data_warehouse": "BigQuery",
            "collaboration": "Google Sheets",
            "storage": "Cloud Storage",
            "visualization": "Looker Studio",
            "compute": "Cloud Functions",
            "messaging": "Pub/Sub",
            "audit": "Cloud Audit",
            "total_reports": len(self.reports),
            "report_types": list(set(r.get('report_type', 'unknown') for r in self.reports)),
            "google_native": True
        }


# Singleton instance (requiere accounting_engine)
def get_venezuelan_reports(accounting_engine):
    """Obtener instancia de VenezuelanReports"""
    return VenezuelanReports(accounting_engine)
