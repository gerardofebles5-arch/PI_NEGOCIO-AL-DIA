# (π)NAD - Tu Contabilidad en Tres Pasos

Sistema de contabilidad automatizada para PYMES venezolanas con validación profesional.

## Visión General

**(π)NAD** es un sistema de contabilidad automatizada que permite tener control financiero en tiempo real con solo 3 pasos simples:

1. **Recopilar documentos** - Reportes Z, facturas, bases de datos
2. **Cargar al formulario** - Subir archivos al enlace proporcionado
3. **Visualizar dashboard** - Gráficos interactivos de situación financiera

## Características

- **OCR Inteligente:** Extracción automática de datos de documentos usando EasyOCR
- **Validación Profesional:** Cada dato es verificado por un asesor contable
- **Ecosistema Google:** Integración nativa con Forms, Sheets, Drive, Document AI
- **Dashboards Interactivos:** Visualización en tiempo real con Looker Studio
- **Seguridad Garantizada:** Autenticación con Gmail OAuth y cifrado de extremo a extremo
- **Especialización Local:** Optimizado para normas y formatos venezolanos

## Arquitectura

```
(π)NAD/
├── src/
│   ├── ocr/                  # Motor OCR
│   │   └── ocr_engine.py
│   ├── integrations/         # Integraciones Google
│   │   ├── google_forms.py
│   │   └── google_sheets.py
│   ├── auth/                # Autenticación
│   │   └── gmail_oauth.py
│   ├── processing/          # Procesamiento de documentos
│   │   └── document_processor.py
│   ├── validation/          # Validación profesional
│   │   └── professional_validator.py
│   └── dashboard/           # Generación de dashboards
│       └── dashboard_generator.py
├── config/                  # Configuración
│   └── config.py
├── docs/                    # Documentación
├── tests/                   # Pruebas
├── main.py                  # Archivo principal
└── requirements.txt         # Dependencias
```

## Requisitos Previos

- Python 3.11+
- Google Cloud Project con APIs habilitadas
- Credenciales de Google OAuth
- Credenciales de Google Service Account

## Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-repo/nad.git
cd nad
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp config/config.py.example config/config.py
# Editar config/config.py con tus credenciales
```

## Configuración

### Google Cloud Project

1. Crear proyecto en Google Cloud Console
2. Habilitar APIs:
   - Google Forms API
   - Google Sheets API
   - Google Drive API
   - Document AI API
   - Cloud SQL API

### OAuth 2.0

1. Crear credenciales OAuth en Google Cloud Console
2. Configurar Client ID y Client Secret en `config/config.py`
3. Establecer Redirect URI

### Service Account

1. Crear Service Account en Google Cloud Console
2. Descargar archivo JSON de credenciales
3. Guardar en `config/service_account.json`
4. Asignar roles necesarios

## Uso

### Inicializar Sistema

```python
from main import PINADSystem

# Inicializar sistema
system = PINADSystem()

# Configurar recursos de Google
resources = system.setup_google_resources()
```

### Registrar Cliente

```python
client_data = {
    'rif': 'J-12345678-9',
    'name': 'Empresa ABC C.A.',
    'email': 'contacto@empresaabc.com',
    'phone': '+58-414-123-4567',
    'sector': 'comercio',
    'plan': 'professional'
}

client = system.register_client(client_data)
```

### Procesar Documentos

```python
file_paths = [
    'reporte_z.pdf',
    'factura_001.pdf',
    'factura_002.pdf'
]

result = system.process_client_documents(
    client_id=client['client_id'],
    file_paths=file_paths,
    document_type='invoice'
)
```

### Crear Solicitud de Validación

```python
validation = system.create_validation_request(document_id='doc_id')
```

### Generar Dashboard

```python
dashboard = system.generate_client_dashboard(client_id='client_id')
```

### Ejecutar Servidor OAuth

```python
system.run_oauth_server(host='0.0.0.0', port=5000)
```

## Componentes

### OCR Engine

Motor de OCR basado en EasyOCR con especialización en documentos venezolanos:
- Extracción de facturas
- Extracción de Reportes Z
- Soporte para PDF, imágenes y hojas de cálculo

### Google Forms Integration

Creación y gestión de formularios de Google Forms para captura de datos.

### Google Sheets Integration

Gestión de hojas de cálculo como base de datos centralizada.

### Gmail OAuth

Sistema de autenticación obligatoria con Gmail para seguridad.

### Document Processor

Procesamiento de documentos con OCR y validación de datos extraídos.

### Professional Validator

Sistema de validación profesional por asesores contables.

### Dashboard Generator

Generación de dashboards interactivos con métricas financieras.

## Planes

| Plan | Precio | Transacciones | Usuarios | Validación |
|------|--------|---------------|----------|------------|
| Básico | $29/mes | 100 | 1 | 48h |
| Profesional | $79/mes | 500 | 3 | 24h |
| Enterprise | $199/mes | Ilimitadas | Ilimitados | 4h |

## Documentación

- [Documentación Completa](./DOCUMENTACION_COMPLETA_PI_NAD.md)
- [Especificaciones de API](./API_SPECIFICATIONS_PI_NAD.md)
- [Guía de Usuario](./GUIA_USUARIO_PI_NAD.md)
- [Guía de Implementación Técnica](./GUIA_IMPLEMENTACION_TECNICA_PI_NAD.md)
- [Plan de Marketing y Ventas](./PLAN_MARKETING_VENTAS_PI_NAD.md)
- [Resumen Ejecutivo](./RESUMEN_EJECUTIVO_PI_NAD.md)

## Roadmap

### Fase 1 (Q1 2026)
- MVP con Google Forms y Sheets
- Procesamiento OCR básico
- 50 clientes iniciales

### Fase 2 (Q2 2026)
- Looker Studio dashboards
- Validación profesional
- 200 clientes

### Fase 3 (Q3 2026)
- Google Document AI
- Automatización con Python
- 500 clientes

### Fase 4 (Q4 2026)
- App móvil Flutter
- API REST
- 1,000 clientes

## Contribución

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

MIT License - Ver archivo LICENSE para detalles

## Contacto

- **Email:** contacto@pinad.com
- **Web:** https://pinad.com
- **Soporte:** soporte@pinad.com

## Créditos

- OCR Engine basado en EasyOCR
- Integración con Google Cloud Platform
- Diseño inspirado en mejores prácticas de SaaS

---

**(π)NAD - Tu Contabilidad en Tres Pasos: Menos Papelería, Más Control**
