"""
Módulo de Compliance Global
Implementa estándares NIIF/NICSP, reportes ESG y pirámide de calidad
"""

from .global_standards import (
    IFRSStandard,
    IPSASStandard,
    ESGCategory,
    ESGMetric,
    QualityLevel,
    ComplianceCheck,
    ESGReport,
    QualityAssessment,
    GlobalComplianceManager,
    global_compliance_manager
)

__all__ = [
    'IFRSStandard',
    'IPSASStandard',
    'ESGCategory',
    'ESGMetric',
    'QualityLevel',
    'ComplianceCheck',
    'ESGReport',
    'QualityAssessment',
    'GlobalComplianceManager',
    'global_compliance_manager'
]
