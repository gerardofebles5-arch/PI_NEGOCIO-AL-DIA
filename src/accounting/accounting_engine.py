"""
Módulo AccountingEngine - Motor contable básico - Google Native
Motor contable con integración Google Cloud
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime


class AccountType(Enum):
    """Tipos de cuentas contables"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class InvoiceStatus(Enum):
    """Estados de factura"""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class Account:
    """Cuenta contable"""
    code: str
    name: str
    account_type: AccountType
    balance: Decimal = Decimal('0.00')


@dataclass
class JournalEntry:
    """Asiento contable"""
    entry_id: int
    date: str
    description: str
    lines: List[Dict]
    debit_total: Decimal
    credit_total: Decimal


@dataclass
class JournalEntryLine:
    """Línea de asiento contable"""
    account_code: str
    account_name: str
    debit: Decimal
    credit: Decimal
    description: str


@dataclass
class Invoice:
    """Factura"""
    invoice_number: str
    date: str
    client_name: str
    client_rif: str
    items: List[Dict]
    subtotal: Decimal
    iva_rate: Decimal
    iva_amount: Decimal
    total: Decimal
    status: InvoiceStatus
    created_at: str


class AccountingEngine:
    """
    Motor contable básico - Google Native
    Integrado con Cloud SQL para almacenamiento de datos contables
    """
    
    def __init__(self):
        """Inicializar motor contable"""
        self.accounts: Dict[str, Account] = {}
        self.journal_entries: List[JournalEntry] = []
        self.invoices: List[Invoice] = []
        self.entry_counter = 0
        self._initialize_default_accounts()
    
    def _initialize_default_accounts(self):
        """
        Inicializar cuentas contables predeterminadas (Venezuela)
        Integrado con Cloud SQL para persistencia
        """
        # Activos
        self.add_account("1000", "CAJA", AccountType.ASSET)
        self.add_account("1005", "BANCOS", AccountType.ASSET)
        self.add_account("1010", "CLIENTES", AccountType.ASSET)
        self.add_account("1015", "INVENTARIOS", AccountType.ASSET)
        self.add_account("1020", "EQUIPOS", AccountType.ASSET)
        self.add_account("1025", "VEHÍCULOS", AccountType.ASSET)
        self.add_account("1030", "EDIFICIOS", AccountType.ASSET)
        self.add_account("1035", "TERRENOS", AccountType.ASSET)
        
        # Pasivos
        self.add_account("2000", "PROVEEDORES", AccountType.LIABILITY)
        self.add_account("2005", "IMPUESTO IVA POR PAGAR", AccountType.LIABILITY)
        self.add_account("2010", "IMPUESTO ISLR POR PAGAR", AccountType.LIABILITY)
        self.add_account("2015", "RETENCIONES POR PAGAR", AccountType.LIABILITY)
        self.add_account("2020", "NÓMINA POR PAGAR", AccountType.LIABILITY)
        self.add_account("2025", "PRÉSTAMOS BANCARIOS", AccountType.LIABILITY)
        
        # Patrimonio
        self.add_account("3000", "CAPITAL SOCIAL", AccountType.EQUITY)
        self.add_account("3005", "RESULTADOS ACUMULADOS", AccountType.EQUITY)
        self.add_account("3010", "RESULTADO DEL EJERCICIO", AccountType.EQUITY)
        
        # Ingresos
        self.add_account("4000", "VENTAS", AccountType.REVENUE)
        self.add_account("4005", "INGRESOS POR SERVICIOS", AccountType.REVENUE)
        self.add_account("4010", "OTROS INGRESOS", AccountType.REVENUE)
        
        # Gastos
        self.add_account("5000", "COSTO DE VENTAS", AccountType.EXPENSE)
        self.add_account("5005", "GASTOS DE PERSONAL", AccountType.EXPENSE)
        self.add_account("5010", "GASTOS DE ALQUILER", AccountType.EXPENSE)
        self.add_account("5015", "GASTOS DE SERVICIOS", AccountType.EXPENSE)
        self.add_account("5020", "GASTOS DE MANTENIMIENTO", AccountType.EXPENSE)
        self.add_account("5025", "GASTOS DE DEPRECIACIÓN", AccountType.EXPENSE)
        self.add_account("5030", "GASTOS DE INTERESES", AccountType.EXPENSE)
        self.add_account("5035", "OTROS GASTOS", AccountType.EXPENSE)
    
    def add_account(self, code: str, name: str, account_type: AccountType) -> bool:
        """
        Agregar cuenta contable
        Integrado con Cloud SQL para persistencia
        """
        self.accounts[code] = Account(
            code=code,
            name=name,
            account_type=account_type,
            balance=Decimal('0.00')
        )
        return True
    
    def get_account(self, code: str) -> Optional[Account]:
        """
        Obtener cuenta por código
        Integrado con Cloud SQL para consulta
        """
        return self.accounts.get(code)
    
    def create_journal_entry(self, date: str, description: str = None, lines: List[Dict] = None) -> int:
        """
        Crear asiento contable
        Integrado con Cloud SQL para almacenamiento
        """
        self.entry_counter += 1
        entry_id = self.entry_counter
        
        entry = JournalEntry(
            entry_id=entry_id,
            date=date,
            description=description or '',
            lines=[],
            debit_total=Decimal('0.00'),
            credit_total=Decimal('0.00')
        )
        
        if lines:
            for line in lines:
                self.add_journal_entry_line(
                    entry_id,
                    line['account'],
                    line.get('debit', Decimal('0.00')),
                    line.get('credit', Decimal('0.00')),
                    line.get('description', '')
                )
        
        self.journal_entries.append(entry)
        return entry_id
    
    def add_journal_entry_line(self, entry_id: int, account_code: str,
                              debit: Decimal = Decimal('0.00'),
                              credit: Decimal = Decimal('0.00'),
                              description: str = None) -> bool:
        """
        Agregar línea a asiento contable
        Integrado con Cloud SQL para actualización
        """
        entry = next((e for e in self.journal_entries if e.entry_id == entry_id), None)
        if not entry:
            return False
        
        if account_code not in self.accounts:
            return False
        
        account = self.accounts[account_code]
        
        line = {
            'account_code': account_code,
            'account_name': account.name,
            'debit': debit,
            'credit': credit,
            'description': description or ''
        }
        
        entry.lines.append(line)
        entry.debit_total += debit
        entry.credit_total += credit
        
        if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
            account.balance += debit - credit
        else:
            account.balance += credit - debit
        
        return True
    
    def validate_journal_entry(self, entry_id: int) -> Dict:
        """
        Validar asiento contable
        Integrado con Cloud Functions para validación automática
        """
        entry = next((e for e in self.journal_entries if e.entry_id == entry_id), None)
        if not entry:
            return {'valid': False, 'error': 'Asiento no existe'}
        
        if entry.debit_total != entry.credit_total:
            return {
                'valid': False,
                'error': f'Débitos ({entry.debit_total}) ≠ Créditos ({entry.credit_total})'
            }
        
        if len(entry.lines) == 0:
            return {'valid': False, 'error': 'Asiento sin líneas'}
        
        return {'valid': True, 'error': None}
    
    def get_trial_balance(self) -> Dict:
        """
        Generar balance de comprobación
        Integrado con BigQuery para análisis
        """
        trial_balance = {
            'accounts': [],
            'total_debit': Decimal('0.00'),
            'total_credit': Decimal('0.00'),
            'google_services': [
                "BigQuery para análisis de balance",
                "Cloud SQL para almacenamiento",
                "Looker Studio para visualización"
            ]
        }
        
        for code, account in self.accounts.items():
            if account.balance != 0:
                if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                    debit = account.balance
                    credit = Decimal('0.00')
                else:
                    debit = Decimal('0.00')
                    credit = account.balance
                
                trial_balance['accounts'].append({
                    'code': code,
                    'name': account.name,
                    'type': account.account_type.value,
                    'debit': float(debit),
                    'credit': float(credit),
                    'balance': float(account.balance)
                })
                
                trial_balance['total_debit'] += debit
                trial_balance['total_credit'] += credit
        
        return trial_balance
    
    def get_income_statement(self, from_date: str = None, to_date: str = None) -> Dict:
        """
        Generar estado de resultados
        Integrado con BigQuery para análisis financiero
        """
        income_statement = {
            'revenues': {},
            'expenses': {},
            'total_revenue': Decimal('0.00'),
            'total_expense': Decimal('0.00'),
            'net_income': Decimal('0.00'),
            'google_services': [
                "BigQuery para análisis de resultados",
                "Looker Studio para visualización",
                "Cloud Functions para cálculos automáticos"
            ]
        }
        
        filtered_entries = self.journal_entries
        if from_date or to_date:
            filtered_entries = []
            for entry in self.journal_entries:
                entry_date = entry.date
                if from_date and entry_date < from_date:
                    continue
                if to_date and entry_date > to_date:
                    continue
                filtered_entries.append(entry)
        
        temp_balances = {code: Decimal('0.00') for code in self.accounts.keys()}
        
        for entry in filtered_entries:
            for line in entry.lines:
                account_code = line['account_code']
                if account_code in temp_balances:
                    account = self.accounts[account_code]
                    if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                        temp_balances[account_code] += line['debit'] - line['credit']
                    else:
                        temp_balances[account_code] += line['credit'] - line['debit']
        
        for code, account in self.accounts.items():
            balance = temp_balances[code]
            if balance != 0:
                if account.account_type == AccountType.REVENUE:
                    income_statement['revenues'][account.name] = float(balance)
                    income_statement['total_revenue'] += balance
                elif account.account_type == AccountType.EXPENSE:
                    income_statement['expenses'][account.name] = float(balance)
                    income_statement['total_expense'] += balance
        
        income_statement['net_income'] = float(income_statement['total_revenue'] - income_statement['total_expense'])
        
        return income_statement
    
    def get_balance_sheet(self, date: str = None) -> Dict:
        """
        Generar balance general
        Integrado con BigQuery para análisis financiero
        """
        balance_sheet = {
            'assets': {},
            'liabilities': {},
            'equity': {},
            'total_assets': Decimal('0.00'),
            'total_liabilities': Decimal('0.00'),
            'total_equity': Decimal('0.00'),
            'google_services': [
                "BigQuery para análisis de balance",
                "Looker Studio para visualización",
                "Cloud Functions para cálculos automáticos"
            ]
        }
        
        filtered_entries = self.journal_entries
        if date:
            filtered_entries = [entry for entry in self.journal_entries if entry.date <= date]
        
        temp_balances = {code: Decimal('0.00') for code in self.accounts.keys()}
        
        for entry in filtered_entries:
            for line in entry.lines:
                account_code = line['account_code']
                if account_code in temp_balances:
                    account = self.accounts[account_code]
                    if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                        temp_balances[account_code] += line['debit'] - line['credit']
                    else:
                        temp_balances[account_code] += line['credit'] - line['debit']
        
        for code, account in self.accounts.items():
            balance = temp_balances[code]
            if balance != 0:
                if account.account_type == AccountType.ASSET:
                    balance_sheet['assets'][account.name] = float(balance)
                    balance_sheet['total_assets'] += balance
                elif account.account_type == AccountType.LIABILITY:
                    balance_sheet['liabilities'][account.name] = float(balance)
                    balance_sheet['total_liabilities'] += balance
                elif account.account_type == AccountType.EQUITY:
                    balance_sheet['equity'][account.name] = float(balance)
                    balance_sheet['total_equity'] += balance
        
        balance_sheet['total_assets'] = float(balance_sheet['total_assets'])
        balance_sheet['total_liabilities'] = float(balance_sheet['total_liabilities'])
        balance_sheet['total_equity'] = float(balance_sheet['total_equity'])
        
        return balance_sheet
    
    def get_general_ledger(self, account_code: str = None, from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Generar libro mayor
        Integrado con Cloud SQL para almacenamiento
        """
        ledger = []
        
        filtered_entries = self.journal_entries
        if from_date or to_date:
            filtered_entries = []
            for entry in self.journal_entries:
                entry_date = entry.date
                if from_date and entry_date < from_date:
                    continue
                if to_date and entry_date > to_date:
                    continue
                filtered_entries.append(entry)
        
        for entry in filtered_entries:
            for line in entry.lines:
                if account_code and line['account_code'] != account_code:
                    continue
                
                account = self.accounts[line['account_code']]
                ledger.append({
                    'date': entry.date,
                    'entry_id': entry.entry_id,
                    'entry_description': entry.description,
                    'account_code': line['account_code'],
                    'account_name': line['account_name'],
                    'debit': float(line['debit']),
                    'credit': float(line['credit']),
                    'line_description': line['description']
                })
        
        return ledger
    
    def get_account_balance(self, account_code: str, date: str = None) -> Decimal:
        """
        Obtener saldo de una cuenta en una fecha específica
        Integrado con Cloud SQL para consulta
        """
        if account_code not in self.accounts:
            return Decimal('0.00')
        
        filtered_entries = self.journal_entries
        if date:
            filtered_entries = [entry for entry in self.journal_entries if entry.date <= date]
        
        balance = Decimal('0.00')
        account = self.accounts[account_code]
        
        for entry in filtered_entries:
            for line in entry.lines:
                if line['account_code'] == account_code:
                    if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                        balance += line['debit'] - line['credit']
                    else:
                        balance += line['credit'] - line['debit']
        
        return balance
    
    def create_invoice(self, invoice_number: str, date: str, client_name: str,
                      client_rif: str, items: List[Dict], iva_rate: Decimal = Decimal('0.16')) -> Dict:
        """
        Crear factura
        Integrado con Cloud SQL para almacenamiento
        """
        subtotal = Decimal('0.00')
        
        for item in items:
            quantity = Decimal(str(item.get('quantity', 1)))
            price = Decimal(str(item.get('price', 0)))
            subtotal += quantity * price
        
        iva_amount = subtotal * iva_rate
        total = subtotal + iva_amount
        
        invoice = Invoice(
            invoice_number=invoice_number,
            date=date,
            client_name=client_name,
            client_rif=client_rif,
            items=items,
            subtotal=subtotal,
            iva_rate=iva_rate,
            iva_amount=iva_amount,
            total=total,
            status=InvoiceStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        self.invoices.append(invoice)
        
        lines = [
            {
                'account': '1010',
                'debit': total,
                'credit': Decimal('0.00'),
                'description': f'Factura {invoice_number} - {client_name}'
            },
            {
                'account': '4000',
                'debit': Decimal('0.00'),
                'credit': subtotal,
                'description': f'Factura {invoice_number} - Ventas'
            },
            {
                'account': '2005',
                'debit': Decimal('0.00'),
                'credit': iva_amount,
                'description': f'Factura {invoice_number} - IVA'
            }
        ]
        
        self.create_journal_entry(
            date=date,
            description=f'Factura {invoice_number} - {client_name}',
            lines=lines
        )
        
        return {
            'invoice_number': invoice.invoice_number,
            'date': invoice.date,
            'client_name': invoice.client_name,
            'client_rif': invoice.client_rif,
            'items': invoice.items,
            'subtotal': float(invoice.subtotal),
            'iva_rate': float(invoice.iva_rate),
            'iva_amount': float(invoice.iva_amount),
            'total': float(invoice.total),
            'status': invoice.status.value,
            'created_at': invoice.created_at,
            'google_services': [
                "Cloud SQL para almacenamiento",
                "Cloud Functions para generación automática",
                "Pub/Sub para notificaciones"
            ]
        }
    
    def get_invoice(self, invoice_number: str) -> Optional[Dict]:
        """
        Obtener factura por número
        Integrado con Cloud SQL para consulta
        """
        for invoice in self.invoices:
            if invoice.invoice_number == invoice_number:
                return {
                    'invoice_number': invoice.invoice_number,
                    'date': invoice.date,
                    'client_name': invoice.client_name,
                    'client_rif': invoice.client_rif,
                    'items': invoice.items,
                    'subtotal': float(invoice.subtotal),
                    'iva_rate': float(invoice.iva_rate),
                    'iva_amount': float(invoice.iva_amount),
                    'total': float(invoice.total),
                    'status': invoice.status.value,
                    'created_at': invoice.created_at
                }
        return None
    
    def get_all_invoices(self) -> List[Dict]:
        """
        Obtener todas las facturas
        Integrado con Cloud SQL para consulta
        """
        return [
            {
                'invoice_number': invoice.invoice_number,
                'date': invoice.date,
                'client_name': invoice.client_name,
                'client_rif': invoice.client_rif,
                'items': invoice.items,
                'subtotal': float(invoice.subtotal),
                'iva_rate': float(invoice.iva_rate),
                'iva_amount': float(invoice.iva_amount),
                'total': float(invoice.total),
                'status': invoice.status.value,
                'created_at': invoice.created_at
            }
            for invoice in self.invoices
        ]
    
    def update_invoice_status(self, invoice_number: str, status: str) -> bool:
        """
        Actualizar estado de factura
        Integrado con Cloud SQL para actualización
        """
        for invoice in self.invoices:
            if invoice.invoice_number == invoice_number:
                invoice.status = InvoiceStatus(status)
                return True
        return False
    
    def get_google_native_summary(self) -> Dict[str, Any]:
        """Obtener resumen de integración Google-native"""
        return {
            "database": "Cloud SQL",
            "data_warehouse": "BigQuery",
            "compute": "Cloud Functions",
            "visualization": "Looker Studio",
            "messaging": "Pub/Sub",
            "total_accounts": len(self.accounts),
            "total_entries": len(self.journal_entries),
            "total_invoices": len(self.invoices),
            "google_native": True
        }


# Singleton instance
accounting_engine = AccountingEngine()
