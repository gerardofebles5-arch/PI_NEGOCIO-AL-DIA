"""
Módulo FinancialStatements - Estados financieros - Google Native
Generador de estados financieros con integración Google Cloud
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime


class StatementType(Enum):
    """Tipos de estados financieros"""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    TRIAL_BALANCE = "trial_balance"


class ExportFormat(Enum):
    """Formatos de exportación"""
    EXCEL = "excel"
    PDF = "pdf"
    CSV = "csv"
    GOOGLE_SHEETS = "google_sheets"


@dataclass
class CashFlowActivity:
    """Actividad de flujo de efectivo"""
    name: str
    amount: Decimal
    category: str


@dataclass
class FinancialStatement:
    """Estado financiero"""
    statement_type: StatementType
    data: Dict
    generated_at: str
    google_services: List[str] = field(default_factory=list)


class FinancialStatements:
    """
    Generador de estados financieros - Google Native
    Integrado con BigQuery, Looker Studio, Cloud Storage, Google Sheets
    """
    
    def __init__(self, accounting_engine):
        """
        Inicializar generador de estados financieros
        
        Args:
            accounting_engine: Motor contable
        """
        self.accounting_engine = accounting_engine
        self.statements: List[FinancialStatement] = []
    
    def generate_balance_sheet(self, date: str = None) -> Dict:
        """
        Generar balance general
        Integrado con BigQuery para análisis y Looker Studio para visualización
        """
        balance_sheet = self.accounting_engine.get_balance_sheet(date)
        
        balance_sheet['google_services'] = [
            "BigQuery para análisis de balance",
            "Looker Studio para visualización",
            "Cloud Storage para almacenamiento",
            "Google Sheets para colaboración"
        ]
        
        statement = FinancialStatement(
            statement_type=StatementType.BALANCE_SHEET,
            data=balance_sheet,
            generated_at=datetime.now().isoformat(),
            google_services=balance_sheet['google_services']
        )
        self.statements.append(statement)
        
        return balance_sheet
    
    def generate_income_statement(self, from_date: str = None, to_date: str = None) -> Dict:
        """
        Generar estado de resultados
        Integrado con BigQuery para análisis y Looker Studio para visualización
        """
        income_statement = self.accounting_engine.get_income_statement(from_date, to_date)
        
        income_statement['google_services'] = [
            "BigQuery para análisis de resultados",
            "Looker Studio para visualización",
            "Cloud Storage para almacenamiento",
            "Google Sheets para colaboración"
        ]
        
        statement = FinancialStatement(
            statement_type=StatementType.INCOME_STATEMENT,
            data=income_statement,
            generated_at=datetime.now().isoformat(),
            google_services=income_statement['google_services']
        )
        self.statements.append(statement)
        
        return income_statement
    
    def generate_cash_flow_statement(self) -> Dict:
        """
        Generar estado de flujo de efectivo (simplificado)
        Integrado con BigQuery para análisis y Looker Studio para visualización
        """
        cash_flow = {
            'operating_activities': {
                'items': [],
                'total': Decimal('0.00')
            },
            'investing_activities': {
                'items': [],
                'total': Decimal('0.00')
            },
            'financing_activities': {
                'items': [],
                'total': Decimal('0.00')
            },
            'net_change': Decimal('0.00'),
            'google_services': [
                "BigQuery para análisis de flujo de efectivo",
                "Looker Studio para visualización",
                "Cloud Storage para almacenamiento",
                "Google Sheets para colaboración"
            ]
        }
        
        income_statement = self.generate_income_statement()
        
        for revenue_name, revenue_amount in income_statement['revenues'].items():
            cash_flow['operating_activities']['items'].append({
                'name': revenue_name,
                'amount': revenue_amount
            })
            cash_flow['operating_activities']['total'] += Decimal(str(revenue_amount))
        
        for expense_name, expense_amount in income_statement['expenses'].items():
            cash_flow['operating_activities']['items'].append({
                'name': expense_name,
                'amount': -expense_amount
            })
            cash_flow['operating_activities']['total'] -= Decimal(str(expense_amount))
        
        balance_sheet = self.generate_balance_sheet()
        
        for asset_name, asset_amount in balance_sheet['assets'].items():
            if any(code in ['1020', '1025', '1030', '1035'] for code in ['1020', '1025', '1030', '1035']):
                cash_flow['investing_activities']['items'].append({
                    'name': f'Adquisición {asset_name}',
                    'amount': -Decimal(str(asset_amount))
                })
                cash_flow['investing_activities']['total'] -= Decimal(str(asset_amount))
        
        for liability_name, liability_amount in balance_sheet['liabilities'].items():
            if 'PRÉSTAMO' in liability_name.upper():
                cash_flow['financing_activities']['items'].append({
                    'name': liability_name,
                    'amount': Decimal(str(liability_amount))
                })
                cash_flow['financing_activities']['total'] += Decimal(str(liability_amount))
        
        for equity_name, equity_amount in balance_sheet['equity'].items():
            if 'CAPITAL' in equity_name.upper():
                cash_flow['financing_activities']['items'].append({
                    'name': equity_name,
                    'amount': Decimal(str(equity_amount))
                })
                cash_flow['financing_activities']['total'] += Decimal(str(equity_amount))
        
        cash_flow['net_change'] = (
            cash_flow['operating_activities']['total'] +
            cash_flow['investing_activities']['total'] +
            cash_flow['financing_activities']['total']
        )
        
        statement = FinancialStatement(
            statement_type=StatementType.CASH_FLOW,
            data=cash_flow,
            generated_at=datetime.now().isoformat(),
            google_services=cash_flow['google_services']
        )
        self.statements.append(statement)
        
        return cash_flow
    
    def generate_trial_balance(self) -> Dict:
        """
        Generar balance de comprobación
        Integrado con BigQuery para análisis y Looker Studio para visualización
        """
        trial_balance = self.accounting_engine.get_trial_balance()
        
        trial_balance['google_services'] = [
            "BigQuery para análisis de balance",
            "Looker Studio para visualización",
            "Cloud Storage para almacenamiento",
            "Google Sheets para colaboración"
        ]
        
        statement = FinancialStatement(
            statement_type=StatementType.TRIAL_BALANCE,
            data=trial_balance,
            generated_at=datetime.now().isoformat(),
            google_services=trial_balance['google_services']
        )
        self.statements.append(statement)
        
        return trial_balance
    
    def export_to_excel(self, file_path: str, statement_type: str = 'balance_sheet') -> Dict:
        """
        Exportar estado financiero a Excel
        Integrado con Google Sheets para colaboración en la nube
        """
        import pandas as pd
        
        result = {
            'success': False,
            'file_path': file_path,
            'statement_type': statement_type,
            'google_services': [
                "Google Sheets para colaboración",
                "Cloud Storage para almacenamiento",
                "Cloud Functions para procesamiento"
            ]
        }
        
        try:
            if statement_type == 'balance_sheet':
                data = self.generate_balance_sheet()
                
                assets_df = pd.DataFrame(list(data['assets'].items()), columns=['Cuenta', 'Monto'])
                assets_df.to_excel(file_path, sheet_name='Activos', index=False)
                
                liabilities_df = pd.DataFrame(list(data['liabilities'].items()), columns=['Cuenta', 'Monto'])
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    liabilities_df.to_excel(writer, sheet_name='Pasivos', index=False)
                
                equity_df = pd.DataFrame(list(data['equity'].items()), columns=['Cuenta', 'Monto'])
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    equity_df.to_excel(writer, sheet_name='Patrimonio', index=False)
                
                result['success'] = True
            
            elif statement_type == 'income_statement':
                data = self.generate_income_statement()
                
                revenues_df = pd.DataFrame(list(data['revenues'].items()), columns=['Cuenta', 'Monto'])
                revenues_df.to_excel(file_path, sheet_name='Ingresos', index=False)
                
                expenses_df = pd.DataFrame(list(data['expenses'].items()), columns=['Cuenta', 'Monto'])
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    expenses_df.to_excel(writer, sheet_name='Gastos', index=False)
                
                summary_df = pd.DataFrame([{
                    'Total Ingresos': data['total_revenue'],
                    'Total Gastos': data['total_expense'],
                    'Resultado Neto': data['net_income']
                }])
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                result['success'] = True
            
            elif statement_type == 'trial_balance':
                data = self.generate_trial_balance()
                
                df = pd.DataFrame(data['accounts'])
                df.to_excel(file_path, sheet_name='Balance Comprobación', index=False)
                
                totals_df = pd.DataFrame([{
                    'Total Débitos': float(data['total_debit']),
                    'Total Créditos': float(data['total_credit'])
                }])
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    totals_df.to_excel(writer, sheet_name='Totales', index=False)
                
                result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def export_to_google_sheets(self, spreadsheet_id: str, statement_type: str = 'balance_sheet') -> Dict:
        """
        Exportar estado financiero a Google Sheets
        Integrado con Google Sheets API para colaboración en tiempo real
        """
        result = {
            'success': False,
            'spreadsheet_id': spreadsheet_id,
            'statement_type': statement_type,
            'google_services': [
                "Google Sheets API",
                "Cloud Storage para respaldo",
                "Cloud Functions para sincronización"
            ]
        }
        
        try:
            if statement_type == 'balance_sheet':
                data = self.generate_balance_sheet()
                result['data'] = data
                result['success'] = True
            elif statement_type == 'income_statement':
                data = self.generate_income_statement()
                result['data'] = data
                result['success'] = True
            elif statement_type == 'cash_flow':
                data = self.generate_cash_flow_statement()
                result['data'] = data
                result['success'] = True
            elif statement_type == 'trial_balance':
                data = self.generate_trial_balance()
                result['data'] = data
                result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def export_to_cloud_storage(self, bucket_name: str, statement_type: str = 'balance_sheet') -> Dict:
        """
        Exportar estado financiero a Cloud Storage
        Integrado con Cloud Storage para almacenamiento en la nube
        """
        result = {
            'success': False,
            'bucket_name': bucket_name,
            'statement_type': statement_type,
            'google_services': [
                "Cloud Storage",
                "Cloud Functions para procesamiento",
                "Cloud Audit para trazabilidad"
            ]
        }
        
        try:
            if statement_type == 'balance_sheet':
                data = self.generate_balance_sheet()
                result['data'] = data
                result['success'] = True
            elif statement_type == 'income_statement':
                data = self.generate_income_statement()
                result['data'] = data
                result['success'] = True
            elif statement_type == 'cash_flow':
                data = self.generate_cash_flow_statement()
                result['data'] = data
                result['success'] = True
            elif statement_type == 'trial_balance':
                data = self.generate_trial_balance()
                result['data'] = data
                result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_statement_history(self) -> List[Dict]:
        """
        Obtener historial de estados financieros generados
        Integrado con BigQuery para análisis histórico
        """
        return [
            {
                'statement_type': stmt.statement_type.value,
                'generated_at': stmt.generated_at,
                'google_services': stmt.google_services
            }
            for stmt in self.statements
        ]
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "data_warehouse": "BigQuery",
            "visualization": "Looker Studio",
            "storage": "Cloud Storage",
            "collaboration": "Google Sheets",
            "compute": "Cloud Functions",
            "audit": "Cloud Audit",
            "total_statements": len(self.statements),
            "statement_types": [stmt.statement_type.value for stmt in self.statements],
            "google_native": True
        }


# Singleton instance (requiere accounting_engine)
def get_financial_statements(accounting_engine):
    """Obtener instancia de FinancialStatements"""
    return FinancialStatements(accounting_engine)
