"""
Paquete principal de (π)NAD - Google Native Architecture
Sistema unificado de contabilidad, valoración de activos, OCR, impuestos, automatización e infraestructura
"""

__version__ = '1.0.0'
__author__ = '(π)NAD Team'
__google_native__ = True

# Módulos de valoración de activos
from .asset_valuation import (
    digital_assets_manager,
    ai_appraisal_manager,
    report_generator
)

# Módulos de contabilidad
from .accounting import (
    ven_nif_validator,
    plan_unico_cuentas_manager,
    enterprise_accounting,
    accounting_advanced,
    accounting_engine,
    get_financial_statements,
    ledger,
    get_venezuelan_reports
)

# Módulos de roadmap
from .roadmap import (
    roadmap_manager
)

# Módulos de OCR
from .ocr import (
    ocr_ultra_advanced_manager
)

# Módulos de impuestos
from .tax import (
    advanced_tax_system
)

# Módulos de automatización
from .automation import (
    alert_system,
    email_watcher,
    file_watcher
)

# Módulos de infraestructura
from .infrastructure import (
    enterprise_infrastructure_manager,
    infrastructure_advanced
)

# Módulos de API
from .api.rest_api import PINADAPI

# Módulos de utilidades
from .utils import utils_manager

__all__ = [
    # Asset Valuation
    'digital_assets_manager',
    'ai_appraisal_manager',
    'report_generator',
    # Accounting
    'ven_nif_validator',
    'plan_unico_cuentas_manager',
    'enterprise_accounting',
    'accounting_advanced',
    'accounting_engine',
    'get_financial_statements',
    'ledger',
    'get_venezuelan_reports',
    # Roadmap
    'roadmap_manager',
    # OCR
    'ocr_ultra_advanced_manager',
    # Tax
    'advanced_tax_system',
    # Automation
    'alert_system',
    'email_watcher',
    'file_watcher',
    # Infrastructure
    'enterprise_infrastructure_manager',
    'infrastructure_advanced',
    # API
    'PINADAPI',
    # Utils
    'utils_manager'
]
