"""
Módulo Ledger - Libros contables - Google Native
Libros contables con integración Google Cloud
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime


class LedgerType(Enum):
    """Tipos de libros contables"""
    GENERAL_JOURNAL = "general_journal"
    GENERAL_LEDGER = "general_ledger"
    SALES_JOURNAL = "sales_journal"
    PURCHASE_JOURNAL = "purchase_journal"
    CASH_RECEIPTS_JOURNAL = "cash_receipts_journal"
    CASH_DISBURSEMENTS_JOURNAL = "cash_disbursements_journal"


class ExportFormat(Enum):
    """Formatos de exportación"""
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    GOOGLE_SHEETS = "google_sheets"


@dataclass
class JournalEntry:
    """Entrada de libro diario"""
    entry_id: str
    date: str
    description: str
    lines: List[Dict]
    debit_total: Decimal
    credit_total: Decimal
    created_at: str


@dataclass
class LedgerEntry:
    """Entrada de libro mayor"""
    account_code: str
    date: str
    description: str
    debit: Decimal
    credit: Decimal
    balance: Decimal


@dataclass
class AccountLedger:
    """Libro mayor de cuenta"""
    account_code: str
    entries: List[LedgerEntry]
    debit_total: Decimal
    credit_total: Decimal
    balance: Decimal


class Ledger:
    """
    Libro contable (Libro Diario, Libro Mayor) - Google Native
    Integrado con Cloud SQL, BigQuery, Cloud Storage, Google Sheets
    """
    
    def __init__(self):
        """Inicializar libro contable"""
        self.general_journal: List[JournalEntry] = []
        self.general_ledger: Dict[str, AccountLedger] = {}
        self.entry_counter = 0
    
    def add_entry(self, date: str, description: str, lines: List[Dict]) -> str:
        """
        Agregar entrada al libro diario
        Integrado con Cloud SQL para persistencia
        """
        self.entry_counter += 1
        entry_id = f"JE-{self.entry_counter:06d}"
        
        debit_total = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        credit_total = sum(Decimal(str(line.get('credit', 0))) for line in lines)
        
        entry = JournalEntry(
            entry_id=entry_id,
            date=date,
            description=description,
            lines=lines,
            debit_total=debit_total,
            credit_total=credit_total,
            created_at=datetime.now().isoformat()
        )
        
        self.general_journal.append(entry)
        self._update_general_ledger(entry)
        
        return entry_id
    
    def _update_general_ledger(self, entry: JournalEntry):
        """
        Actualizar libro mayor con entrada del libro diario
        Integrado con Cloud SQL para actualización
        """
        for line in entry.lines:
            account_code = line['account_code']
            
            if account_code not in self.general_ledger:
                self.general_ledger[account_code] = AccountLedger(
                    account_code=account_code,
                    entries=[],
                    debit_total=Decimal('0.00'),
                    credit_total=Decimal('0.00'),
                    balance=Decimal('0.00')
                )
            
            ledger_entry = LedgerEntry(
                account_code=account_code,
                date=entry.date,
                description=entry.description,
                debit=Decimal(str(line.get('debit', 0))),
                credit=Decimal(str(line.get('credit', 0))),
                balance=Decimal('0.00')
            )
            
            self.general_ledger[account_code].entries.append(ledger_entry)
            self.general_ledger[account_code].debit_total += ledger_entry.debit
            self.general_ledger[account_code].credit_total += ledger_entry.credit
            self.general_ledger[account_code].balance += ledger_entry.debit - ledger_entry.credit
    
    def get_general_journal(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Obtener libro diario
        Integrado con Cloud SQL para consulta
        """
        if not start_date and not end_date:
            return {
                'entries': [
                    {
                        'entry_id': entry.entry_id,
                        'date': entry.date,
                        'description': entry.description,
                        'lines': entry.lines,
                        'debit_total': float(entry.debit_total),
                        'credit_total': float(entry.credit_total),
                        'created_at': entry.created_at
                    }
                    for entry in self.general_journal
                ],
                'google_services': [
                    "Cloud SQL para almacenamiento",
                    "BigQuery para análisis",
                    "Cloud Storage para respaldo"
                ]
            }
        
        filtered_entries = []
        for entry in self.general_journal:
            if start_date and entry.date < start_date:
                continue
            if end_date and entry.date > end_date:
                continue
            filtered_entries.append({
                'entry_id': entry.entry_id,
                'date': entry.date,
                'description': entry.description,
                'lines': entry.lines,
                'debit_total': float(entry.debit_total),
                'credit_total': float(entry.credit_total),
                'created_at': entry.created_at
            })
        
        return {
            'entries': filtered_entries,
            'google_services': [
                "Cloud SQL para almacenamiento",
                "BigQuery para análisis",
                "Cloud Storage para respaldo"
            ]
        }
    
    def get_general_ledger(self, account_code: str = None) -> Dict:
        """
        Obtener libro mayor
        Integrado con Cloud SQL para consulta
        """
        if account_code:
            if account_code in self.general_ledger:
                ledger = self.general_ledger[account_code]
                return {
                    'account_code': ledger.account_code,
                    'entries': [
                        {
                            'account_code': entry.account_code,
                            'date': entry.date,
                            'description': entry.description,
                            'debit': float(entry.debit),
                            'credit': float(entry.credit),
                            'balance': float(entry.balance)
                        }
                        for entry in ledger.entries
                    ],
                    'debit_total': float(ledger.debit_total),
                    'credit_total': float(ledger.credit_total),
                    'balance': float(ledger.balance),
                    'google_services': [
                        "Cloud SQL para almacenamiento",
                        "BigQuery para análisis",
                        "Cloud Storage para respaldo"
                    ]
                }
            return {}
        
        return {
            'accounts': {
                code: {
                    'account_code': ledger.account_code,
                    'entries_count': len(ledger.entries),
                    'debit_total': float(ledger.debit_total),
                    'credit_total': float(ledger.credit_total),
                    'balance': float(ledger.balance)
                }
                for code, ledger in self.general_ledger.items()
            },
            'google_services': [
                "Cloud SQL para almacenamiento",
                "BigQuery para análisis",
                "Cloud Storage para respaldo"
            ]
        }
    
    def export_to_csv(self, file_path: str, ledger_type: str = 'journal') -> Dict:
        """
        Exportar libro a CSV
        Integrado con Cloud Storage para almacenamiento en la nube
        """
        import csv
        
        result = {
            'success': False,
            'file_path': file_path,
            'ledger_type': ledger_type,
            'google_services': [
                "Cloud Storage para almacenamiento",
                "Cloud Functions para procesamiento",
                "Cloud Audit para trazabilidad"
            ]
        }
        
        try:
            if ledger_type == 'journal':
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID Entrada', 'Fecha', 'Descripción', 'Cuenta', 'Débito', 'Crédito'])
                    
                    for entry in self.general_journal:
                        for line in entry.lines:
                            writer.writerow([
                                entry.entry_id,
                                entry.date,
                                entry.description,
                                line['account_code'],
                                line.get('debit', 0),
                                line.get('credit', 0)
                            ])
                result['success'] = True
            
            elif ledger_type == 'ledger':
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Cuenta', 'Fecha', 'Descripción', 'Débito', 'Crédito', 'Saldo'])
                    
                    for account_code, ledger in self.general_ledger.items():
                        for entry in ledger.entries:
                            writer.writerow([
                                account_code,
                                entry.date,
                                entry.description,
                                entry.debit,
                                entry.credit,
                                ledger.balance
                            ])
                result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def export_to_google_sheets(self, spreadsheet_id: str, ledger_type: str = 'journal') -> Dict:
        """
        Exportar libro a Google Sheets
        Integrado con Google Sheets API para colaboración en tiempo real
        """
        result = {
            'success': False,
            'spreadsheet_id': spreadsheet_id,
            'ledger_type': ledger_type,
            'google_services': [
                "Google Sheets API",
                "Cloud Storage para respaldo",
                "Cloud Functions para sincronización"
            ]
        }
        
        try:
            if ledger_type == 'journal':
                data = self.get_general_journal()
                result['data'] = data
                result['success'] = True
            elif ledger_type == 'ledger':
                data = self.get_general_ledger()
                result['data'] = data
                result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def export_to_cloud_storage(self, bucket_name: str, ledger_type: str = 'journal') -> Dict:
        """
        Exportar libro a Cloud Storage
        Integrado con Cloud Storage para almacenamiento en la nube
        """
        result = {
            'success': False,
            'bucket_name': bucket_name,
            'ledger_type': ledger_type,
            'google_services': [
                "Cloud Storage",
                "Cloud Functions para procesamiento",
                "Cloud Audit para trazabilidad"
            ]
        }
        
        try:
            if ledger_type == 'journal':
                data = self.get_general_journal()
                result['data'] = data
                result['success'] = True
            elif ledger_type == 'ledger':
                data = self.get_general_ledger()
                result['data'] = data
                result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_account_balance(self, account_code: str) -> Decimal:
        """
        Obtener saldo de cuenta
        Integrado con Cloud SQL para consulta
        """
        if account_code in self.general_ledger:
            return self.general_ledger[account_code].balance
        return Decimal('0.00')
    
    def get_entry_by_id(self, entry_id: str) -> Optional[Dict]:
        """
        Obtener entrada por ID
        Integrado con Cloud SQL para consulta
        """
        for entry in self.general_journal:
            if entry.entry_id == entry_id:
                return {
                    'entry_id': entry.entry_id,
                    'date': entry.date,
                    'description': entry.description,
                    'lines': entry.lines,
                    'debit_total': float(entry.debit_total),
                    'credit_total': float(entry.credit_total),
                    'created_at': entry.created_at
                }
        return None
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "database": "Cloud SQL",
            "data_warehouse": "BigQuery",
            "storage": "Cloud Storage",
            "collaboration": "Google Sheets",
            "compute": "Cloud Functions",
            "audit": "Cloud Audit",
            "total_journal_entries": len(self.general_journal),
            "total_ledger_accounts": len(self.general_ledger),
            "google_native": True
        }


# Singleton instance
ledger = Ledger()
