"""
Módulo de Flujo Referencial πNAD (Fase 0)
Integra el flujo original de recolección de información como referencia histórica
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class DocumentType(Enum):
    """Tipos de documentos según flujo original πNAD"""
    REPORTE_Z = "reporte_z"
    FACTURAS = "facturas"
    ESTADOS_CUENTA = "estados_cuenta"
    ARCHIVOS_DATOS = "archivos_datos"


class ProcessingPeriod(Enum):
    """Períodos de procesamiento según flujo original"""
    MENSUAL = "mensual"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"


@dataclass
class DocumentSubmission:
    """Solicitud de documento según flujo original πNAD"""
    email: str
    rif: str
    client_name: str
    processing_period: ProcessingPeriod
    document_type: DocumentType
    submission_date: date = field(default_factory=date.today)
    files: List[str] = field(default_factory=list)
    instructions_followed: bool = False
    notes: Optional[str] = None


@dataclass
class SubmissionInstructions:
    """Instrucciones para correcta presentación según flujo original"""
    document_type: DocumentType
    instructions: List[str]
    tips: List[str]
    common_errors: List[str]


class LegacyFlowManager:
    """
    Gestor del flujo referencial πNAD (Fase 0)
    Mantiene el flujo original como referencia histórica y educativa
    """
    
    def __init__(self):
        """Inicializar gestor de flujo legacy"""
        self.submissions: List[DocumentSubmission] = []
        self.instructions_map: Dict[DocumentType, SubmissionInstructions] = {}
        self._initialize_instructions()
    
    def _initialize_instructions(self):
        """Inicializar instrucciones por tipo de documento"""
        self.instructions_map[DocumentType.REPORTE_Z] = SubmissionInstructions(
            document_type=DocumentType.REPORTE_Z,
            instructions=[
                "El Reporte Z debe corresponder al período seleccionado",
                "Incluir todos los reportes Z del período (diarios si es mensual)",
                "Asegurar que los reportes sean legibles",
                "Nombre de archivo debe incluir fecha y establecimiento"
            ],
            tips=[
                "Organizar por fecha cronológica",
                "Verificar que no falten días en el período",
                "Incluir reportes de todos los puntos de venta"
            ],
            common_errors=[
                "Reportes de períodos diferentes mezclados",
                "Falta de reportes de días específicos",
                "Archivos ilegibles o corruptos"
            ]
        )
        
        self.instructions_map[DocumentType.FACTURAS] = SubmissionInstructions(
            document_type=DocumentType.FACTURAS,
            instructions=[
                "Incluir todas las facturas emitidas y recibidas del período",
                "Facturas deben estar numeradas consecutivamente",
                "Incluir facturas de compra y venta",
                "Verificar que estén completas (todas las páginas)"
            ],
            tips=[
                "Separar facturas emitidas de recibidas",
                "Organizar por fecha y número",
                "Incluir notas de débito y crédito"
            ],
            common_errors=[
                "Falta de facturas del período",
                "Facturas sin número o fecha",
                "Facturas incompletas"
            ]
        )
        
        self.instructions_map[DocumentType.ESTADOS_CUENTA] = SubmissionInstructions(
            document_type=DocumentType.ESTADOS_CUENTA,
            instructions=[
                "Incluir estados de cuenta de todas las cuentas bancarias",
                "Debe cubrir el período completo seleccionado",
                "Estados deben ser oficiales del banco",
                "Incluir cuentas corrientes y de ahorro"
            ],
            tips=[
                "Descargar directamente del portal bancario",
                "Verificar que incluya movimientos del primer y último día",
                "Incluir cuentas de todas las entidades bancarias"
            ],
            common_errors=[
                "Estados de cuenta incompletos",
                "Períodos que no coinciden",
                "Falta de cuentas bancarias"
            ]
        )
        
        self.instructions_map[DocumentType.ARCHIVOS_DATOS] = SubmissionInstructions(
            document_type=DocumentType.ARCHIVOS_DATOS,
            instructions=[
                "Archivos deben estar en formato compatible (Excel, CSV)",
                "Incluir todas las columnas requeridas",
                "Datos deben corresponder al período seleccionado",
                "Verificar que no haya errores de formato"
            ],
            tips=[
                "Usar plantillas proporcionadas si están disponibles",
                "Validar datos antes de enviar",
                "Incluir archivo de descripción de columnas"
            ],
            common_errors=[
                "Formatos no compatibles",
                "Columnas faltantes o incorrectas",
                "Datos fuera del período"
            ]
        )
    
    def get_instructions(self, document_type: DocumentType) -> SubmissionInstructions:
        """Obtener instrucciones para tipo de documento"""
        return self.instructions_map.get(document_type)
    
    def create_submission(self, email: str, rif: str, client_name: str,
                         processing_period: ProcessingPeriod,
                         document_type: DocumentType,
                         files: List[str] = None,
                         notes: str = None) -> DocumentSubmission:
        """
        Crear nueva solicitud de documento
        (Referencial - en producción esto se integra con Google Forms)
        """
        submission = DocumentSubmission(
            email=email,
            rif=rif,
            client_name=client_name,
            processing_period=processing_period,
            document_type=document_type,
            files=files or [],
            notes=notes
        )
        self.submissions.append(submission)
        return submission
    
    def validate_submission(self, submission: DocumentSubmission) -> Dict[str, Any]:
        """
        Validar solicitud según reglas del flujo original
        """
        errors = []
        warnings = []
        
        # Validar RIF
        if not submission.rif or len(submission.rif) < 10:
            errors.append("RIF inválido o incompleto")
        
        # Validar email
        if not submission.email or "@" not in submission.email:
            errors.append("Email inválido")
        
        # Validar archivos
        if not submission.files:
            warnings.append("No se han cargado archivos")
        
        # Validar instrucciones
        instructions = self.get_instructions(submission.document_type)
        if instructions:
            if not submission.instructions_followed:
                warnings.append("No se ha confirmado seguimiento de instrucciones")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "submission_id": f"{submission.rif}_{submission.submission_date.isoformat()}"
        }
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen del flujo referencial
        """
        return {
            "flow_name": "πNAD (Fase 0) - Sistema Provisional",
            "flow_description": "Flujo original de recolección de documentos via Google Forms",
            "document_types": [dt.value for dt in DocumentType],
            "processing_periods": [pp.value for pp in ProcessingPeriod],
            "total_submissions": len(self.submissions),
            "submissions_by_type": {
                dt.value: len([s for s in self.submissions if s.document_type == dt])
                for dt in DocumentType
            },
            "integration_note": "Este flujo se mantiene como referencia histórica. "
                               "En producción se usa API REST + Google Cloud Storage."
        }
    
    def get_google_forms_integration_guide(self) -> Dict[str, Any]:
        """
        Guía de integración con Google Forms (referencial)
        """
        return {
            "integration_type": "Google Forms + Google Drive + Google Sheets",
            "current_implementation": "API REST + Google Cloud Storage",
            "legacy_flow_steps": [
                "1. Cliente recibe email de confirmación",
                "2. Cliente completa Google Forms con RIF, período, tipo de documento",
                "3. Cliente carga archivos en Google Drive",
                "4. Datos se registran en Google Sheets",
                "5. Sistema procesa documentos automáticamente"
            ],
            "current_implementation_steps": [
                "1. Cliente usa API REST o dashboard web",
                "2. Sistema valida datos en tiempo real",
                "3. Archivos se almacenan en Google Cloud Storage",
                "4. Datos se registran en Cloud SQL",
                "5. Sistema procesa con Google Document AI"
            ],
            "migration_benefits": [
                "Validación en tiempo real",
                "Mayor seguridad con Cloud Storage",
                "Escalabilidad automática",
                "Integración con Document AI para OCR",
                "API para integraciones de terceros"
            ]
        }


# Singleton instance
legacy_flow_manager = LegacyFlowManager()
