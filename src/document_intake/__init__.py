"""
Módulo de Intake de Documentos
Integra flujo referencial πNAD (Fase 0) y sistemas modernos de recolección
"""

from .legacy_flow import (
    DocumentType,
    ProcessingPeriod,
    DocumentSubmission,
    SubmissionInstructions,
    LegacyFlowManager,
    legacy_flow_manager
)

__all__ = [
    'DocumentType',
    'ProcessingPeriod',
    'DocumentSubmission',
    'SubmissionInstructions',
    'LegacyFlowManager',
    'legacy_flow_manager'
]
