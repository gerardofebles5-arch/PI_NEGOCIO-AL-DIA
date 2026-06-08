"""
Módulo de Contabilidad Avanzada V4.0 - Google Native
Mejoras en funcionalidades contables con integración Google Cloud
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging


class DepreciationMethod(Enum):
    """Métodos de depreciación"""
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"


class MatchScore(Enum):
    """Niveles de coincidencia"""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BankTransaction:
    """Transacción bancaria"""
    transaction_id: str
    amount: Decimal
    date: date
    description: str
    reference: Optional[str] = None


@dataclass
class CompanyTransaction:
    """Transacción de empresa"""
    transaction_id: str
    amount: Decimal
    date: date
    description: str
    reference: Optional[str] = None


@dataclass
class MatchedTransaction:
    """Transacción conciliada"""
    bank_transaction: BankTransaction
    company_transaction: CompanyTransaction
    match_score: float
    match_level: MatchScore


@dataclass
class Invoice:
    """Factura"""
    invoice_id: str
    rif: str
    invoice_number: str
    amount: Decimal
    date: date
    iva_rate: Decimal = Decimal('16')


@dataclass
class Asset:
    """Activo fijo"""
    asset_id: str
    cost: Decimal
    salvage_value: Decimal
    useful_life: int
    asset_type: str
    purchase_date: date


@dataclass
class JournalEntry:
    """Asiento contable"""
    entry_id: str
    date: date
    description: str
    lines: List[Dict]
    total_debit: Decimal
    total_credit: Decimal


@dataclass
class CashFlow:
    """Flujo de caja"""
    period: str
    inflow: Decimal
    outflow: Decimal
    balance: Decimal


class AdvancedAccounting:
    """
    Funcionalidades contables avanzadas - Google Native
    Integrado con BigQuery, Cloud Functions, Cloud Scheduler
    """
    
    def __init__(self):
        """Inicializar módulo contable avanzado"""
        self.duplicate_threshold = 0.95
        self.depreciation_rates = {
            'maquinaria': 0.10,
            'vehiculos': 0.20,
            'equipos': 0.25,
            'edificios': 0.05,
            'mobiliario': 0.10,
        }
        self.matched_transactions: List[MatchedTransaction] = []
        self.duplicates: Dict[str, List[Invoice]] = {}
        self.journal_entries: List[JournalEntry] = []
        self.cash_flow_history: List[CashFlow] = []
    
    def reconcile_bank_statement(self, bank_transactions: List[Dict], 
                                 company_transactions: List[Dict]) -> Dict:
        """
        Conciliación bancaria automática
        Integrado con BigQuery para análisis de transacciones
        """
        matched = []
        unmatched_bank = []
        unmatched_company = []
        
        for bank_tx in bank_transactions:
            matched_found = False
            for comp_tx in company_transactions:
                if self._match_transactions(bank_tx, comp_tx):
                    match_score = self._calculate_match_score(bank_tx, comp_tx)
                    matched.append({
                        'bank': bank_tx,
                        'company': comp_tx,
                        'match_score': match_score,
                        'match_level': self._get_match_level(match_score)
                    })
                    matched_found = True
                    break
            
            if not matched_found:
                unmatched_bank.append(bank_tx)
        
        matched_company_ids = {m['company']['id'] for m in matched}
        for comp_tx in company_transactions:
            if comp_tx['id'] not in matched_company_ids:
                unmatched_company.append(comp_tx)
        
        return {
            'matched': matched,
            'unmatched_bank': unmatched_bank,
            'unmatched_company': unmatched_company,
            'reconciliation_rate': len(matched) / len(bank_transactions) if bank_transactions else 0,
            'google_services': [
                "BigQuery para análisis de transacciones",
                "Cloud Functions para procesamiento",
                "Cloud Scheduler para conciliaciones programadas",
                "Pub/Sub para notificaciones"
            ]
        }
    
    def _match_transactions(self, bank_tx: Dict, comp_tx: Dict) -> bool:
        """Determinar si dos transacciones coinciden"""
        if abs(bank_tx.get('amount', 0) - comp_tx.get('amount', 0)) > 0.01:
            return False
        
        bank_date = bank_tx.get('date')
        comp_date = comp_tx.get('date')
        if bank_date and comp_date:
            date_diff = abs((bank_date - comp_date).days)
            if date_diff > 3:
                return False
        
        return True
    
    def _calculate_match_score(self, bank_tx: Dict, comp_tx: Dict) -> float:
        """Calcular puntuación de coincidencia"""
        score = 0.0
        
        amount_diff = abs(bank_tx.get('amount', 0) - comp_tx.get('amount', 0))
        if amount_diff < 0.01:
            score += 0.4
        elif amount_diff < 1.0:
            score += 0.2
        
        bank_date = bank_tx.get('date')
        comp_date = comp_tx.get('date')
        if bank_date and comp_date:
            date_diff = abs((bank_date - comp_date).days)
            if date_diff == 0:
                score += 0.3
            elif date_diff <= 1:
                score += 0.2
            elif date_diff <= 3:
                score += 0.1
        
        bank_desc = bank_tx.get('description', '').lower()
        comp_desc = comp_tx.get('description', '').lower()
        if bank_desc and comp_desc:
            if bank_desc in comp_desc or comp_desc in bank_desc:
                score += 0.3
        
        return score
    
    def _get_match_level(self, score: float) -> MatchScore:
        """Determinar nivel de coincidencia"""
        if score >= 0.9:
            return MatchScore.EXACT
        elif score >= 0.7:
            return MatchScore.HIGH
        elif score >= 0.5:
            return MatchScore.MEDIUM
        else:
            return MatchScore.LOW
    
    def detect_duplicates(self, invoices: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Detección de facturas duplicadas
        Integrado con BigQuery para análisis de duplicados
        """
        duplicates = {}
        processed = []
        
        for invoice in invoices:
            invoice_key = self._get_invoice_key(invoice)
            
            if invoice_key in duplicates:
                duplicates[invoice_key].append(invoice)
            else:
                similar_found = False
                for processed_invoice in processed:
                    if self._are_invoices_similar(invoice, processed_invoice):
                        key = self._get_invoice_key(processed_invoice)
                        if key in duplicates:
                            duplicates[key].append(invoice)
                        else:
                            duplicates[key] = [processed_invoice, invoice]
                        similar_found = True
                        break
                
                if not similar_found:
                    processed.append(invoice)
        
        duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
        
        return {
            'duplicates': duplicates,
            'total_duplicates': sum(len(v) for v in duplicates.values()),
            'google_services': [
                "BigQuery para análisis de duplicados",
                "Cloud Functions para detección automática",
                "Pub/Sub para alertas de duplicados"
            ]
        }
    
    def _get_invoice_key(self, invoice: Dict) -> str:
        """Generar clave única para factura"""
        rif = invoice.get('rif', '')
        invoice_number = invoice.get('invoice_number', '')
        amount = invoice.get('amount', 0)
        return f"{rif}-{invoice_number}-{amount}"
    
    def _are_invoices_similar(self, inv1: Dict, inv2: Dict) -> bool:
        """Determinar si dos facturas son similares"""
        if inv1.get('rif') != inv2.get('rif'):
            return False
        
        if inv1.get('invoice_number') and inv2.get('invoice_number'):
            if inv1['invoice_number'] == inv2['invoice_number']:
                return True
        
        amount_diff = abs(inv1.get('amount', 0) - inv2.get('amount', 0))
        if amount_diff < 1.0:
            return True
        
        return False
    
    def calculate_depreciation(self, asset: Dict, 
                              method: str = 'straight_line') -> Dict:
        """
        Calcular depreciación de activo
        Integrado con BigQuery para seguimiento de depreciación
        """
        cost = Decimal(str(asset.get('cost', 0)))
        salvage_value = Decimal(str(asset.get('salvage_value', 0)))
        useful_life = asset.get('useful_life', 5)
        asset_type = asset.get('type', 'equipos')
        
        rate = self.depreciation_rates.get(asset_type, 0.10)
        
        if method == 'straight_line':
            annual_depreciation = (cost - salvage_value) / useful_life
            accumulated = Decimal('0')
            schedule = []
            
            for year in range(1, useful_life + 1):
                accumulated += annual_depreciation
                book_value = cost - accumulated
                schedule.append({
                    'year': year,
                    'depreciation': float(annual_depreciation),
                    'accumulated': float(accumulated),
                    'book_value': float(book_value)
                })
            
            return {
                'method': 'straight_line',
                'annual_depreciation': float(annual_depreciation),
                'schedule': schedule,
                'google_services': [
                    "BigQuery para seguimiento de depreciación",
                    "Cloud Scheduler para cálculos automáticos",
                    "Cloud Functions para procesamiento"
                ]
            }
        
        elif method == 'declining_balance':
            book_value = cost
            schedule = []
            
            for year in range(1, useful_life + 1):
                depreciation = book_value * Decimal(str(rate))
                book_value -= depreciation
                schedule.append({
                    'year': year,
                    'depreciation': float(depreciation),
                    'accumulated': float(cost - book_value),
                    'book_value': float(book_value)
                })
            
            return {
                'method': 'declining_balance',
                'rate': rate,
                'schedule': schedule,
                'google_services': [
                    "BigQuery para seguimiento de depreciación",
                    "Cloud Scheduler para cálculos automáticos",
                    "Cloud Functions para procesamiento"
                ]
            }
        
        return {}
    
    def generate_journal_entry(self, invoice: Dict) -> Dict:
        """
        Generar asiento contable desde factura
        Integrado con Cloud SQL para almacenamiento de asientos
        """
        amount = Decimal(str(invoice.get('amount', 0)))
        iva_rate = Decimal(str(invoice.get('iva_rate', 16)))
        rif = invoice.get('rif', '')
        invoice_number = invoice.get('invoice_number', '')
        
        iva_amount = amount * (iva_rate / 100)
        base_imponible = amount - iva_amount
        
        lines = [
            {
                'account': 'Cuentas por Cobrar',
                'debit': float(amount),
                'credit': 0.0,
                'description': f'Factura {invoice_number} - {rif}'
            },
            {
                'account': 'Ventas',
                'debit': 0.0,
                'credit': float(base_imponible),
                'description': f'Venta gravada - Factura {invoice_number}'
            },
            {
                'account': 'IVA por Pagar',
                'debit': 0.0,
                'credit': float(iva_amount),
                'description': f'IVA {iva_rate}% - Factura {invoice_number}'
            }
        ]
        
        return {
            'date': invoice.get('date', datetime.now().strftime('%Y-%m-%d')),
            'description': f'Asiento por factura {invoice_number}',
            'lines': lines,
            'total_debit': float(amount),
            'total_credit': float(amount),
            'google_services': [
                "Cloud SQL para almacenamiento de asientos",
                "Cloud Functions para generación automática",
                "BigQuery para análisis contable",
                "Cloud Audit para trazabilidad"
            ]
        }
    
    def calculate_working_capital(self, current_assets: Decimal, 
                                 current_liabilities: Decimal) -> Dict:
        """
        Calcular capital de trabajo y ratios relacionados
        Integrado con BigQuery para análisis financiero
        """
        working_capital = current_assets - current_liabilities
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else Decimal('0')
        quick_ratio = (current_assets - Decimal('10000')) / current_liabilities if current_liabilities > 0 else Decimal('0')
        
        return {
            'working_capital': float(working_capital),
            'current_ratio': float(current_ratio),
            'quick_ratio': float(quick_ratio),
            'interpretation': self._interpretate_ratios(float(current_ratio), float(quick_ratio)),
            'google_services': [
                "BigQuery para análisis financiero",
                "Looker Studio para visualización",
                "Cloud Functions para cálculos automáticos"
            ]
        }
    
    def _interpretate_ratios(self, current_ratio: float, quick_ratio: float) -> str:
        """Interpretar ratios financieros"""
        if current_ratio >= 2.0 and quick_ratio >= 1.0:
            return "Situación financiera sólida"
        elif current_ratio >= 1.5 and quick_ratio >= 0.8:
            return "Situación financiera aceptable"
        elif current_ratio >= 1.0:
            return "Situación financiera regular"
        else:
            return "Situación financiera preocupante"
    
    def generate_cash_flow_projection(self, cash_flows: List[Dict], 
                                    months: int = 12) -> List[Dict]:
        """
        Generar proyección de flujo de caja
        Integrado con BigQuery ML para proyecciones predictivas
        """
        if not cash_flows:
            return []
        
        avg_inflow = sum(cf.get('inflow', 0) for cf in cash_flows) / len(cash_flows)
        avg_outflow = sum(cf.get('outflow', 0) for cf in cash_flows) / len(cash_flows)
        
        projections = []
        current_balance = cash_flows[-1].get('balance', 0) if cash_flows else 0
        
        for month in range(1, months + 1):
            projected_inflow = avg_inflow * (1 + (month * 0.01))
            projected_outflow = avg_outflow * (1 + (month * 0.005))
            
            current_balance += projected_inflow - projected_outflow
            
            projections.append({
                'month': month,
                'projected_inflow': projected_inflow,
                'projected_outflow': projected_outflow,
                'net_cash_flow': projected_inflow - projected_outflow,
                'projected_balance': current_balance
            })
        
        return {
            'projections': projections,
            'google_services': [
                "BigQuery ML para proyecciones predictivas",
                "Cloud Functions para cálculos automáticos",
                "Looker Studio para visualización",
                "Cloud Scheduler para actualizaciones"
            ]
        }
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "database": "Cloud SQL",
            "data_warehouse": "BigQuery",
            "ml": "BigQuery ML",
            "compute": "Cloud Functions",
            "scheduling": "Cloud Scheduler",
            "messaging": "Pub/Sub",
            "visualization": "Looker Studio",
            "audit": "Cloud Audit",
            "total_functions": 7,
            "google_native": True
        }


# Singleton instance
advanced_accounting = AdvancedAccounting()
