"""
Módulo de Impuestos
Integra cálculos de impuestos avanzados con arquitectura Google-native
"""

from .tax_advanced import (
    TaxType,
    DeclarationStatus,
    TaxRate,
    TaxDeclaration,
    TaxPenalty,
    TaxProjection,
    TaxObligation,
    AdvancedTaxSystem,
    advanced_tax_system
)

__all__ = [
    'TaxType',
    'DeclarationStatus',
    'TaxRate',
    'TaxDeclaration',
    'TaxPenalty',
    'TaxProjection',
    'TaxObligation',
    'AdvancedTaxSystem',
    'advanced_tax_system'
]
