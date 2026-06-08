# Cloud Functions Python - OCR Ultra Avanzado

## Descripción
Este directorio contiene las Cloud Functions en Python para el motor OCR ultra avanzado V5.0 integrado con Google Document AI.

## Archivos

### ocr_ultra.py
Implementación del motor OCR ultra avanzado con 20 funciones principales:
- OCR de facturas con plantillas específicas
- Reconocimiento de sellos y firmas
- OCR de documentos manuscritos
- Reconocimiento de tablas complejas
- OCR de documentos con fondo complejo
- Detección de documentos falsificados
- Validación de RIF en tiempo real
- Verificación de consistencia matemática
- Detección de documentos duplicados
- Scoring de calidad del documento
- Extracción de datos de PDFs escaneados
- Reconocimiento de zonas de firma
- OCR de documentos en múltiples idiomas
- Clasificación por tipo de documento
- Extracción de líneas de detalle
- OCR incremental
- Previsualización de extracción
- Batch processing con progreso
- Auto-corrección de errores comunes
- Exportación de resultados en tiempo real

### main.py
Punto de entrada principal para las Cloud Functions.

### requirements.txt
Dependencias de Python necesarias para el funcionamiento de las Cloud Functions.

### deploy_ocr_ultra.sh
Script de bash para desplegar la Cloud Function en Google Cloud.

## Funciones Disponibles

### process_document_ultra
Procesa un documento con todas las mejoras ultra del motor OCR.

**Endpoint:** `POST /process_document_ultra`

**Request Body:**
```json
{
  "document_path": "ruta/al/documento",
  "template_name": "banesco",
  "options": {}
}
```

**Response:**
```json
{
  "timestamp": "2024-12-25T00:00:00",
  "processing_steps": [
    "quality_assessment",
    "background_processing",
    "signature_detection",
    "table_recognition",
    "line_item_extraction",
    "auto_correction",
    "consistency_verification",
    "forgery_detection"
  ],
  "quality": {
    "overall_score": 85,
    "clarity": 90,
    "contrast": 80,
    "noise_level": 85,
    "text_density": 85,
    "recommendations": ["Mejorar iluminación", "Aumentar resolución"]
  },
  "signatures": [...],
  "tables": {...},
  "line_items": [...],
  "consistency": {...},
  "forgery_check": {...},
  "overall_confidence": 0.85,
  "google_native": true
}
```

### extract_with_template
Extrae datos de un documento usando una plantilla específica.

**Endpoint:** `POST /extract_with_template`

**Request Body:**
```json
{
  "document_path": "ruta/al/documento",
  "template_name": "banesco"
}
```

**Response:**
```json
{
  "template_used": "banesco",
  "rif": "J-12345678-9",
  "invoice_number": "001",
  "date": "25/12/2024",
  "amount": "1000.00",
  "confidence": 0.95,
  "google_services": [
    "Google Document AI",
    "Cloud Storage para almacenamiento",
    "Cloud Functions para procesamiento"
  ]
}
```

### get_ocr_summary
Obtiene un resumen del motor OCR y sus capacidades.

**Endpoint:** `GET /get_ocr_summary`

**Response:**
```json
{
  "ocr_engine": "Google Document AI",
  "ai_platform": "Vertex AI",
  "storage": "Cloud Storage",
  "compute": "Cloud Functions",
  "queue": "Cloud Tasks",
  "messaging": "Pub/Sub",
  "audit": "Cloud Audit",
  "monitoring": "Cloud Monitoring",
  "total_functions": 120,
  "accuracy": "95%+",
  "languages_supported": ["es", "en", "pt"],
  "document_types": 13,
  "google_native": true
}
```

## Plantillas Disponibles

### banesco
Plantilla para facturas de Banesco.

**Patrones:**
- RIF: `RIF[:\s]*([JGVE]-\d{8}-\d)`
- Número de factura: `N[úu]mero[:\s]*(\d+)`
- Fecha: `(\d{2}/\d{2}/\d{4})`
- Monto: `BS[:\s]*([\d.,]+)`

### mercantil
Plantilla para facturas de Mercantil.

**Patrones:**
- RIF: `R\.I\.F\.[:\s]*([JGVE]-\d{8}-\d)`
- Número de factura: `Factura[:\s]*N[º°]\s*(\d+)`
- Fecha: `(\d{2}/\d{2}/\d{4})`
- Monto: `Total[:\s]*BS[:\s]*([\d.,]+)`

### provincial
Plantilla para facturas de Provincial.

**Patrones:**
- RIF: `RIF[:\s]*([JGVE]-\d{8}-\d)`
- Número de factura: `N[úu]mero[:\s]*(\d+)`
- Fecha: `(\d{2}/\d{2}/\d{4})`
- Monto: `Monto[:\s]*([\d.,]+)`

## Despliegue

### Prerrequisitos
- Google Cloud SDK instalado
- Proyecto de Google Cloud configurado
- Python 3.10+ instalado

### Pasos de Despliegue

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
export PROJECT_ID="pinad-project"
export REGION="us-central1"
```

3. **Desplegar la Cloud Function:**
```bash
chmod +x deploy_ocr_ultra.sh
./deploy_ocr_ultra.sh
```

O manualmente:
```bash
gcloud functions deploy process_document_ultra \
  --gen2 \
  --runtime=python310 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_document_ultra \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512MB \
  --timeout=60s \
  --max-instances=10 \
  --project=pinad-project
```

## Configuración de Google Cloud

### Document AI
1. Crear un processor en Document AI
2. Configurar el processor ID en las variables de entorno
3. Habilitar la API de Document AI

### Vertex AI
1. Habilitar la API de Vertex AI
2. Configurar modelos de clasificación si es necesario
3. Configurar endpoints de predicción

### Cloud Storage
1. Crear bucket para almacenamiento de documentos
2. Configurar permisos de acceso
3. Configurar reguras de ciclo de vida

### Secret Manager
1. Crear secretos para API keys
2. Configurar permisos de acceso
3. Configurar rotación de secretos

## Monitoreo

### Cloud Monitoring
Las Cloud Functions envían métricas a Cloud Monitoring automáticamente:
- Latencia de invocación
- Tasa de errores
- Uso de memoria
- Uso de CPU

### Cloud Logging
Los logs se envían a Cloud Logging:
- Logs de invocación
- Logs de errores
- Logs de depuración

### Cloud Trace
Las trazas se envían a Cloud Trace para análisis de rendimiento.

## Seguridad

### IAM Roles
- **Cloud Functions Invoker**: Permite invocar la función
- **Cloud Functions Viewer**: Permite ver logs y métricas
- **Storage Object Viewer**: Permite acceder a documentos en Cloud Storage
- **Document AI User**: Permite usar Document AI
- **Vertex AI User**: Permite usar Vertex AI

### Secret Manager
Las API keys y credenciales se almacenan en Secret Manager:
- API key de SENIAT
- Credenciales de Document AI
- Credenciales de Vertex AI

## Costos

### Precios Estimados
- **Cloud Functions**: $0.40 por millón de invocaciones
- **Document AI**: $1.50 por página (procesamiento)
- **Cloud Storage**: $0.026 por GB/mes
- **Vertex AI**: $0.10 por hora de entrenamiento
- **Secret Manager**: $0.06 por 10,000 accesos

### Optimización de Costos
- Usar caché para documentos duplicados
- Procesamiento incremental para documentos grandes
- Batch processing para múltiples documentos
- Configurar límites de memoria y timeout apropiados

## Soporte

Para problemas o preguntas:
1. Revisar logs en Cloud Logging
2. Revisar métricas en Cloud Monitoring
3. Revisar trazas en Cloud Trace
4. Consultar documentación de Google Cloud

## Licencia
Copyright © 2024 (π)NAD - Contabilidad Automatizada con Google Cloud
