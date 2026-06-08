"""
Módulo de Plan Único de Cuentas del Sector Público Venezolano
Integra clasificador presupuestario completo con normas, reglas y valores tributarios
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import date
from decimal import Decimal


class AccountGroup(Enum):
    """Grupos principales del Plan Único de Cuentas"""
    ACTIVOS = "1.00.00.00.00"  # Activos
    PASIVOS = "2.00.00.00.00"  # Pasivos
    RECURSOS = "3.00.00.00.00"  # Recursos
    EGRESOS = "4.00.00.00.00"  # Egresos
    RESULTADOS = "5.00.00.00.00"  # Resultados
    PATRIMONIO = "6.00.00.00.00"  # Patrimonio-Capital
    CUENTAS_ORDEN = "7.00.00.00.00"  # Cuentas de Orden


class AccountLevel(Enum):
    """Niveles de desagregación"""
    RUBRO = "rubro"  # X.01.00.00.00
    GENERICO = "generico"  # X.01.01.00.00
    ESPECIFICO = "especifico"  # X.01.01.01.00
    SUB_ESPECIFICO = "sub_especifico"  # X.01.01.01.01


class ResourceType(Enum):
    """Tipos de recursos (Grupo 3)"""
    INGRESOS_ORDINARIOS = "3.01.00.00.00"
    INGRESOS_EXTRAORDINARIOS = "3.02.00.00.00"
    INGRESOS_OPERACION = "3.03.00.00.00"
    INGRESOS_AJENOS_OPERACION = "3.04.00.00.00"
    TRANSFERENCIAS = "3.05.00.00.00"
    RECURSOS_PROPIOS_CAPITAL = "3.06.00.00.00"
    DISMINUCION_ACTIVOS_FINANCIEROS = "3.07.00.00.00"
    INCREMENTO_PASIVOS = "3.08.00.00.00"
    INCREMENTO_PATRIMONIO = "3.09.00.00.00"
    DEVOLUCION_FONDOS = "3.10.00.00.00"


class ExpenseType(Enum):
    """Tipos de egresos (Grupo 4)"""
    GASTOS_PERSONAL = "4.01.00.00.00"
    MATERIALES_SUMINISTROS = "4.02.00.00.00"
    SERVICIOS_NO_PERSONALES = "4.03.00.00.00"
    ACTIVOS_REALES = "4.04.00.00.00"
    ACTIVOS_FINANCIEROS = "4.05.00.00.00"
    SERVICIO_DEUDA_PUBLICA = "4.06.00.00.00"
    TRANSFERENCIA = "4.07.00.00.00"
    GASTOS_INSTITUCIONES_DESCENTRALIZADAS = "4.08.00.00.00"
    DISMINUCION_PATRIMONIO = "4.09.00.00.00"
    GASTOS_INDEMNIZACIONES_SANCIONES = "4.10.00.00.00"
    GASTOS_DEFENSA_SEGURIDAD = "4.51.00.00.00"
    ASIGNACIONES_NO_DISTRIBUIDAS = "4.52.00.00.00"
    RECTIFICACIONES_PRESUPUESTO = "4.98.00.00.00"


@dataclass
class AccountCode:
    """Cuenta del Plan Único de Cuentas"""
    code: str
    description: str
    group: AccountGroup
    level: AccountLevel
    tax_rate: Optional[Decimal] = None
    rules: List[str] = field(default_factory=list)
    google_services: List[str] = field(default_factory=list)


@dataclass
class BudgetEntry:
    """Asignación presupuestaria"""
    account_code: str
    budgeted_amount: Decimal
    executed_amount: Decimal = Decimal('0')
    available_amount: Decimal = field(init=False)
    execution_percentage: float = field(init=False)
    
    def __post_init__(self):
        self.available_amount = self.budgeted_amount - self.executed_amount
        self.execution_percentage = (self.executed_amount / self.budgeted_amount * 100) if self.budgeted_amount else 0


@dataclass
class TaxRule:
    """Regla tributaria"""
    tax_type: str
    rate: Decimal
    base: str
    exemptions: List[str]
    calculation_method: str
    google_automation: str


class PlanUnicoCuentasManager:
    """
    Gestor del Plan Único de Cuentas
    Implementa clasificador presupuestario completo con arquitectura Google-native
    """
    
    def __init__(self):
        """Inicializar gestor del Plan Único de Cuentas"""
        self.account_codes: Dict[str, AccountCode] = {}
        self.budget_entries: Dict[str, BudgetEntry] = {}
        self.tax_rules: Dict[str, TaxRule] = {}
        self._initialize_account_codes()
        self._initialize_tax_rules()
    
    def _initialize_account_codes(self):
        """Inicializar códigos de cuenta principales"""
        # Grupo 1: Activos
        self.account_codes["1.01.00.00.00"] = AccountCode(
            code="1.01.00.00.00",
            description="Activo Corriente",
            group=AccountGroup.ACTIVOS,
            level=AccountLevel.RUBRO,
            google_services=["BigQuery", "Cloud SQL"]
        )
        
        # Grupo 2: Pasivos
        self.account_codes["2.01.00.00.00"] = AccountCode(
            code="2.01.00.00.00",
            description="Pasivo Corriente",
            group=AccountGroup.PASIVOS,
            level=AccountLevel.RUBRO,
            google_services=["BigQuery", "Cloud SQL"]
        )
        
        # Grupo 3: Recursos
        for resource_type in ResourceType:
            self.account_codes[resource_type.value] = AccountCode(
                code=resource_type.value,
                description=resource_type.name.replace("_", " ").title(),
                group=AccountGroup.RECURSOS,
                level=AccountLevel.RUBRO,
                google_services=["BigQuery", "Looker Studio"]
            )
        
        # Grupo 4: Egresos
        for expense_type in ExpenseType:
            tax_rate = self._get_tax_rate_for_expense(expense_type)
            self.account_codes[expense_type.value] = AccountCode(
                code=expense_type.value,
                description=expense_type.name.replace("_", " ").title(),
                group=AccountGroup.EGRESOS,
                level=AccountLevel.RUBRO,
                tax_rate=tax_rate,
                rules=self._get_rules_for_expense(expense_type),
                google_services=["BigQuery", "Cloud Functions", "Vertex AI"]
            )
        
        # Grupo 5: Resultados
        self.account_codes["5.01.00.00.00"] = AccountCode(
            code="5.01.00.00.00",
            description="Resultados del Ejercicio",
            group=AccountGroup.RESULTADOS,
            level=AccountLevel.RUBRO,
            google_services=["BigQuery", "Looker Studio"]
        )
        
        # Grupo 6: Patrimonio
        self.account_codes["6.01.00.00.00"] = AccountCode(
            code="6.01.00.00.00",
            description="Patrimonio",
            group=AccountGroup.PATRIMONIO,
            level=AccountLevel.RUBRO,
            google_services=["BigQuery", "Cloud SQL"]
        )
        
        # Grupo 7: Cuentas de Orden
        self.account_codes["7.01.00.00.00"] = AccountCode(
            code="7.01.00.00.00",
            description="Cuentas de Orden",
            group=AccountGroup.CUENTAS_ORDEN,
            level=AccountLevel.RUBRO,
            google_services=["BigQuery", "Cloud Logging"]
        )
    
    def _get_tax_rate_for_expense(self, expense_type: ExpenseType) -> Optional[Decimal]:
        """Obtener tasa impositiva para tipo de egreso"""
        tax_rates = {
            ExpenseType.GASTOS_PERSONAL: Decimal('0.16'),  # 16% IVA
            ExpenseType.MATERIALES_SUMINISTROS: Decimal('0.16'),
            ExpenseType.SERVICIOS_NO_PERSONALES: Decimal('0.16'),
            ExpenseType.ACTIVOS_REALES: Decimal('0.16'),
            ExpenseType.ACTIVOS_FINANCIEROS: Decimal('0.00'),
            ExpenseType.SERVICIO_DEUDA_PUBLICA: Decimal('0.00'),
            ExpenseType.TRANSFERENCIA: Decimal('0.00'),
            ExpenseType.GASTOS_INSTITUCIONES_DESCENTRALIZADAS: Decimal('0.16'),
            ExpenseType.DISMINUCION_PATRIMONIO: Decimal('0.00'),
            ExpenseType.GASTOS_INDEMNIZACIONES_SANCIONES: Decimal('0.00'),
            ExpenseType.GASTOS_DEFENSA_SEGURIDAD: Decimal('0.00'),
            ExpenseType.ASIGNACIONES_NO_DISTRIBUIDAS: Decimal('0.00'),
            ExpenseType.RECTIFICACIONES_PRESUPUESTO: Decimal('0.00')
        }
        return tax_rates.get(expense_type)
    
    def _get_rules_for_expense(self, expense_type: ExpenseType) -> List[str]:
        """Obtener reglas para tipo de egreso"""
        rules_map = {
            ExpenseType.GASTOS_PERSONAL: [
                "Retención ISLR según tabla",
                "Aportes patronales SS",
                "Retención IVA si aplica",
                "Registro en nómina"
            ],
            ExpenseType.MATERIALES_SUMINISTROS: [
                "Retención IVA 75% o 100%",
                "Comprobante fiscal",
                "Registro de inventario"
            ],
            ExpenseType.SERVICIOS_NO_PERSONALES: [
                "Retención ISLR según servicio",
                "Retención IVA 75% o 100%",
                "Comprobante fiscal"
            ],
            ExpenseType.ACTIVOS_REALES: [
                "Retención IVA según activo",
                "Depreciación según NIIF",
                "Registro de activo fijo"
            ]
        }
        return rules_map.get(expense_type, [])
    
    def _initialize_tax_rules(self):
        """Inicializar reglas tributarias"""
        self.tax_rules["iva"] = TaxRule(
            tax_type="IVA",
            rate=Decimal('0.16'),
            base="Base imponible",
            exemptions=["Servicios exentos", "Bienes exentos"],
            calculation_method="Porcentaje sobre base imponible",
            google_automation="Cloud Functions con Vertex AI"
        )
        
        self.tax_rules["isrl"] = TaxRule(
            tax_type="ISLR",
            rate=Decimal('0.34'),
            base="Renta gravable",
            exemptions=["Exenciones personales", "Deducciones permitidas"],
            calculation_method="Escala progresiva según tabla",
            google_automation="Cloud Functions con Vertex AI"
        )
        
        self.tax_rules["patronal"] = TaxRule(
            tax_type="Aportes Patronales",
            rate=Decimal('0.12'),
            base="Nómina bruta",
            exemptions=["None"],
            calculation_method="Porcentaje sobre nómina",
            google_automation="Cloud Functions automatizado"
        )
    
    def create_budget_entry(self, account_code: str, 
                           budgeted_amount: Decimal) -> BudgetEntry:
        """Crear asignación presupuestaria"""
        if account_code not in self.account_codes:
            raise ValueError(f"Account code {account_code} not found")
        
        entry = BudgetEntry(
            account_code=account_code,
            budgeted_amount=budgeted_amount
        )
        self.budget_entries[account_code] = entry
        return entry
    
    def execute_budget(self, account_code: str, 
                      executed_amount: Decimal) -> BudgetEntry:
        """Ejecutar presupuesto"""
        if account_code not in self.budget_entries:
            raise ValueError(f"Budget entry {account_code} not found")
        
        entry = self.budget_entries[account_code]
        entry.executed_amount += executed_amount
        entry.available_amount = entry.budgeted_amount - entry.executed_amount
        entry.execution_percentage = (entry.executed_amount / entry.budgeted_amount * 100) if entry.budgeted_amount else 0
        return entry
    
    def calculate_tax(self, tax_type: str, base_amount: Decimal) -> Decimal:
        """Calcular impuesto según regla tributaria"""
        if tax_type not in self.tax_rules:
            raise ValueError(f"Tax rule {tax_type} not found")
        
        rule = self.tax_rules[tax_type]
        return base_amount * rule.rate
    
    def get_account_code(self, code: str) -> Optional[AccountCode]:
        """Obtener código de cuenta"""
        return self.account_codes.get(code)
    
    def get_budget_summary(self) -> Dict[str, Any]:
        """Obtener resumen presupuestario"""
        total_budgeted = sum(e.budgeted_amount for e in self.budget_entries.values())
        total_executed = sum(e.executed_amount for e in self.budget_entries.values())
        total_available = sum(e.available_amount for e in self.budget_entries.values())
        
        return {
            "total_budgeted": total_budgeted,
            "total_executed": total_executed,
            "total_available": total_available,
            "overall_execution_percentage": (total_executed / total_budgeted * 100) if total_budgeted else 0,
            "entries_by_group": {
                group.value: len([e for e in self.budget_entries.values() 
                                if self.account_codes[e.account_code].group == group])
                for group in AccountGroup
            },
            "google_native_integration": {
                "budget_management": "BigQuery para análisis presupuestario",
                "tax_calculation": "Cloud Functions con Vertex AI",
                "compliance_monitoring": "Cloud Audit para trazabilidad",
                "reporting": "Looker Studio para dashboards",
                "automation": "Cloud Workflows para aprobaciones"
            }
        }
    
    def get_puc_implementation_guide(self) -> Dict[str, Any]:
        """Obtener guía de implementación del Plan Único de Cuentas"""
        return {
            "puc_version": "2002 (Undécima versión)",
            "regulatory_body": "ONAPRE - Oficina Nacional de Presupuesto",
            "legal_basis": "Ley Orgánica de Administración Financiera del Sector Público",
            "account_structure": {
                "total_groups": 7,
                "code_length": 8 positions,
                "levels": 4 (Rubro, Genérico, Específico, Sub-específico)
            },
            "groups": {
                "1.00.00.00.00": "Activos",
                "2.00.00.00.00": "Pasivos",
                "3.00.00.00.00": "Recursos",
                "4.00.00.00.00": "Egresos",
                "5.00.00.00.00": "Resultados",
                "6.00.00.00.00": "Patrimonio-Capital",
                "7.00.00.00.00": "Cuentas de Orden"
            },
            "tax_rates": {
                "IVA": "16% estándar",
                "ISLR": "34% máxima",
                "Aportes Patronales": "12% sobre nómina"
            },
            "google_native_implementation": {
                "data_warehouse": "BigQuery para almacenamiento de datos presupuestarios",
                "tax_automation": "Cloud Functions con Vertex AI para cálculo automático",
                "compliance": "Cloud Audit para verificación de cumplimiento",
                "reporting": "Looker Studio para reportes en tiempo real",
                "integration": "API Gateway para integración con sistemas externos"
            },
            "implementation_phases": [
                "Fase 1: Mapeo de cuentas existentes",
                "Fase 2: Configuración de tasas tributarias",
                "Fase 3: Integración con sistemas de nómina",
                "Fase 4: Automatización de cálculos",
                "Fase 5: Reportes y dashboards"
            ]
        }


# Singleton instance
plan_unico_cuentas_manager = PlanUnicoCuentasManager()
