"""
Módulo Generador de Informes de Avalúo
Implementa generación de informes según formato ideal con arquitectura Google-native
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal


class ReportType(Enum):
    """Tipos de informes de avalúo"""
    TECHNICAL_APPRAISAL = "technical_appraisal"
    COMMERCIAL_APPRAISAL = "commercial_appraisal"
    INDUSTRIAL_APPRAISAL = "industrial_appraisal"
    RESIDENTIAL_APPRAISAL = "residential_appraisal"
    LAND_APPRAISAL = "land_appraisal"


class ValuationMethod(Enum):
    """Métodos de valoración"""
    COST_APPROACH = "cost_approach"
    MARKET_APPROACH = "market_approach"
    INCOME_APPROACH = "income_approach"
    COMPARISON_APPROACH = "comparison_approach"


class ConservationState(Enum):
    """Estado de conservación"""
    EXCELLENT = "excellent"
    GOOD = "good"
    REGULAR = "regular"
    POOR = "poor"
    VERY_POOR = "very_poor"


@dataclass
class AppraiserCertification:
    """Certificación del perito avalúador"""
    appraiser_name: str
    appraiser_id: str
    professional_license: str
    certification_body: str
    certification_date: date
    specialization: str


@dataclass
class PropertyDescription:
    """Descripción detallada de propiedad"""
    property_id: str
    property_type: str
    location: str
    area_sqm: float
    boundaries: str
    zoning: str
    public_services: List[str]
    accessibility: str
    construction_year: Optional[int] = None
    floors: Optional[int] = None
    offices: Optional[int] = None
    bathrooms: Optional[int] = None
    patio_area: Optional[float] = None


@dataclass
class PropertyCharacteristics:
    """Características de la propiedad"""
    structure_type: str
    walls: str
    roof: str
    floors: str
    windows: str
    doors: str
    electrical_installation: str
    plumbing: str
    air_conditioning: Optional[str] = None
    security_system: Optional[str] = None
    parking_spaces: Optional[int] = None


@dataclass
class ConservationAssessment:
    """Evaluación del estado de conservación"""
    general_state: ConservationState
    structure_state: ConservationState
    finishes_state: ConservationState
    installations_state: ConservationState
    observations: List[str]
    maintenance_recommendations: List[str]


@dataclass
class LegalAspects:
    """Aspectos legales"""
    ownership: str
    registration_number: str
    registration_date: date
    encumbrances: List[str]
    restrictions: List[str]
    zoning_compliance: bool
    permits: List[str]


@dataclass
class ValuationCalculation:
    """Cálculo de valoración"""
    method: ValuationMethod
    land_value: Decimal
    construction_value: Decimal
    depreciation_percentage: float
    depreciation_amount: Decimal
    replacement_cost_new: Decimal
    final_valuation: Decimal
    valuation_date: date
    currency: str = "USD"


@dataclass
class AppraisalReport:
    """Informe de avalúo completo"""
    report_id: str
    report_type: ReportType
    property_description: PropertyDescription
    property_characteristics: PropertyCharacteristics
    conservation_assessment: ConservationAssessment
    legal_aspects: LegalAspects
    valuation_calculation: ValuationCalculation
    appraiser_certification: AppraiserCertification
    report_date: date
    google_services: List[str]


class ReportGenerator:
    """
    Generador de Informes de Avalúo
    Implementa generación de informes según formato ideal con arquitectura Google-native
    """
    
    def __init__(self):
        """Inicializar generador de informes"""
        self.reports: Dict[str, AppraisalReport] = {}
        self.report_templates: Dict[ReportType, Dict[str, Any]] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Inicializar plantillas de informe"""
        self.report_templates[ReportType.TECHNICAL_APPRAISAL] = {
            "sections": [
                "Certificación de Peritos",
                "Descripción del Inmueble",
                "Características",
                "Estado de Conservación",
                "Aspectos Legales",
                "Metodología de Valoración",
                "Cálculo de Valor",
                "Conclusiones"
            ],
            "format": "PDF con firma digital",
            "language": "Español"
        }
        
        self.report_templates[ReportType.INDUSTRIAL_APPRAISAL] = {
            "sections": [
                "Certificación de Peritos",
                "Ubicación y Accesibilidad",
                "Descripción del Galpón Industrial",
                "Características Estructurales",
                "Estado de Conservación",
                "Aspectos Legales y Regulatorios",
                "Metodología: Método del Costo",
                "Valor de Reposición Nuevo",
                "Depreciación",
                "Valor Final de Avalúo"
            ],
            "format": "PDF con firma digital",
            "language": "Español"
        }
    
    def create_appraisal_report(self,
                                property_description: PropertyDescription,
                                property_characteristics: PropertyCharacteristics,
                                conservation_assessment: ConservationAssessment,
                                legal_aspects: LegalAspects,
                                valuation_calculation: ValuationCalculation,
                                appraiser_certification: AppraiserCertification,
                                report_type: ReportType = ReportType.TECHNICAL_APPRAISAL) -> AppraisalReport:
        """
        Crear informe de avalúo completo
        (En producción, esto usaría Google Docs API para generación de documentos)
        """
        report_id = f"REP_{property_description.property_id}_{date.today().isoformat()}"
        
        report = AppraisalReport(
            report_id=report_id,
            report_type=report_type,
            property_description=property_description,
            property_characteristics=property_characteristics,
            conservation_assessment=conservation_assessment,
            legal_aspects=legal_aspects,
            valuation_calculation=valuation_calculation,
            appraiser_certification=appraiser_certification,
            report_date=date.today(),
            google_services=[
                "Google Docs API para generación de documentos",
                "Cloud Storage para almacenamiento de informes",
                "Cloud KMS para seguridad de firmas digitales",
                "Cloud Audit para trazabilidad",
                "Looker Studio para visualización de datos"
            ]
        )
        
        self.reports[report_id] = report
        return report
    
    def generate_report_content(self, report: AppraisalReport) -> Dict[str, Any]:
        """Generar contenido del informe"""
        template = self.report_templates.get(report.report_type, {})
        
        content = {
            "report_id": report.report_id,
            "report_type": report.report_type.value,
            "report_date": report.report_date.isoformat(),
            "sections": template.get("sections", []),
            "content": {
                "certification": {
                    "appraiser_name": report.appraiser_certification.appraiser_name,
                    "appraiser_id": report.appraiser_certification.appraiser_id,
                    "professional_license": report.appraiser_certification.professional_license,
                    "certification_body": report.appraiser_certification.certification_body,
                    "certification_date": report.appraiser_certification.certification_date.isoformat(),
                    "specialization": report.appraiser_certification.specialization
                },
                "property_description": {
                    "property_id": report.property_description.property_id,
                    "property_type": report.property_description.property_type,
                    "location": report.property_description.location,
                    "area_sqm": report.property_description.area_sqm,
                    "boundaries": report.property_description.boundaries,
                    "zoning": report.property_description.zoning,
                    "public_services": report.property_description.public_services,
                    "accessibility": report.property_description.accessibility
                },
                "characteristics": {
                    "structure_type": report.property_characteristics.structure_type,
                    "walls": report.property_characteristics.walls,
                    "roof": report.property_characteristics.roof,
                    "floors": report.property_characteristics.floors,
                    "windows": report.property_characteristics.windows,
                    "doors": report.property_characteristics.doors,
                    "electrical_installation": report.property_characteristics.electrical_installation,
                    "plumbing": report.property_characteristics.plumbing
                },
                "conservation": {
                    "general_state": report.conservation_assessment.general_state.value,
                    "structure_state": report.conservation_assessment.structure_state.value,
                    "finishes_state": report.conservation_assessment.finishes_state.value,
                    "installations_state": report.conservation_assessment.installations_state.value,
                    "observations": report.conservation_assessment.observations,
                    "maintenance_recommendations": report.conservation_assessment.maintenance_recommendations
                },
                "legal_aspects": {
                    "ownership": report.legal_aspects.ownership,
                    "registration_number": report.legal_aspects.registration_number,
                    "registration_date": report.legal_aspects.registration_date.isoformat(),
                    "encumbrances": report.legal_aspects.encumbrances,
                    "restrictions": report.legal_aspects.restrictions,
                    "zoning_compliance": report.legal_aspects.zoning_compliance,
                    "permits": report.legal_aspects.permits
                },
                "valuation": {
                    "method": report.valuation_calculation.method.value,
                    "land_value": str(report.valuation_calculation.land_value),
                    "construction_value": str(report.valuation_calculation.construction_value),
                    "depreciation_percentage": report.valuation_calculation.depreciation_percentage,
                    "depreciation_amount": str(report.valuation_calculation.depreciation_amount),
                    "replacement_cost_new": str(report.valuation_calculation.replacement_cost_new),
                    "final_valuation": str(report.valuation_calculation.final_valuation),
                    "valuation_date": report.valuation_calculation.valuation_date.isoformat(),
                    "currency": report.valuation_calculation.currency
                }
            },
            "google_native": True
        }
        
        return content
    
    def export_to_pdf(self, report: AppraisalReport) -> str:
        """
        Exportar informe a PDF
        (En producción, esto usaría Google Docs API para exportar a PDF)
        """
        content = self.generate_report_content(report)
        
        # Simular generación de PDF
        pdf_path = f"/reports/{report.report_id}.pdf"
        
        return pdf_path
    
    def get_report_summary(self) -> Dict[str, Any]:
        """Obtener resumen de informes generados"""
        if not self.reports:
            return {"message": "No reports generated yet"}
        
        total_valued = sum(r.valuation_calculation.final_valuation for r in self.reports.values())
        
        return {
            "total_reports": len(self.reports),
            "total_value_usd": total_valued,
            "reports_by_type": {
                report_type.value: len([r for r in self.reports.values() if r.report_type == report_type])
                for report_type in ReportType
            },
            "reports_by_state": {
                state.value: len([r for r in self.reports.values() 
                                if r.conservation_assessment.general_state == state])
                for state in ConservationState
            },
            "google_native_integration": {
                "document_generation": "Google Docs API",
                "pdf_export": "Google Docs API + Cloud Storage",
                "digital_signature": "Cloud KMS",
                "audit_trail": "Cloud Audit",
                "storage": "Cloud Storage",
                "visualization": "Looker Studio"
            }
        }
    
    def get_ideal_format_reference(self) -> Dict[str, Any]:
        """Obtener referencia del formato ideal de informe"""
        return {
            "reference_document": "INFORME DEFINITIVO - GALPON (MAY2026)",
            "format_ideal": {
                "structure": [
                    "1. Certificación de Peritos Avalúadores",
                    "2. Descripción del Inmueble",
                    "3. Características del Inmueble",
                    "4. Estado de Conservación",
                    "5. Aspectos Legales",
                    "6. Metodología de Valoración",
                    "7. Cálculo de Valor",
                    "8. Conclusiones"
                ],
                "key_elements": [
                    "Identificación clara de peritos con licencias",
                    "Descripción detallada de ubicación y accesibilidad",
                    "Especificación exacta de área y linderos",
                    "Detalle de características estructurales",
                    "Evaluación objetiva del estado de conservación",
                    "Verificación de aspectos legales y registros",
                    "Metodología clara (método del costo)",
                    "Cálculo detallado de valor de reposición",
                    "Aplicación correcta de depreciación",
                    "Valor final con moneda especificada"
                ],
                "professional_standards": [
                    "SOITAVE - Sociedad de Ingenieros de Avalúos de Venezuela",
                    "Normas NIIF para valoración de activos",
                    "Normas venezolanas de avalúo",
                    "Ética profesional y confidencialidad"
                ]
            },
            "google_native_implementation": {
                "template_management": "Google Docs Templates",
                "automation": "Cloud Functions para generación automática",
                "signatures": "Cloud KMS para firmas digitales",
                "distribution": "Gmail API para envío automático",
                "storage": "Cloud Storage con versioning",
                "compliance": "Cloud Audit para trazabilidad regulatoria"
            }
        }


# Singleton instance
report_generator = ReportGenerator()
