# DOCUMENTACIÓN COMPLETA: Sistema (π)NAD - Tu Contabilidad en Tres Pasos

## ÍNDICE

1. [Visión General y Estrategia](#1-visión-general-y-estrategia)
2. [Arquitectura Técnica Detallada](#2-arquitectura-técnica-detallada)
3. [Modelos de Datos y Esquemas](#3-modelos-de-datos-y-esquemas)
4. [Integración con Google Ecosystem](#4-integración-con-google-ecosystem)
5. [Procesos de Negocio Detallados](#5-procesos-de-negocio-detallados)
6. [Casos de Uso y Escenarios](#6-casos-de-uso-y-escenarios)
7. [Roadmap 2026-2027 Detallado](#7-roadmap-2026-2027-detallado)
8. [Arquitectura de Seguridad](#8-arquitectura-de-seguridad)
9. [Estrategia de Implementación](#9-estrategia-de-implementación)
10. [Cumplimiento Normativo](#10-cumplimiento-normativo)
11. [Métricas y KPIs](#11-métricas-y-kpis)
12. [Análisis de Competencia](#12-análisis-de-competencia)

---

## 1. VISIÓN GENERAL Y ESTRATEGIA

### 1.1 Misión

**(π)NAD** tiene como misión transformar la gestión contable tradicional de PYMES venezolanas mediante un sistema automatizado que elimina la transcripción manual de datos, proporciona control financiero en tiempo real y reduce significativamente la carga administrativa, permitiendo a los empresarios enfocarse en hacer crecer su negocio.

### 1.2 Visión

Convertirse en la plataforma líder de contabilidad automatizada en Venezuela, expandiendo posteriormente a otros mercados latinoamericanos, con el objetivo de digitalizar la gestión financiera de más de 100,000 PYMES para 2030.

### 1.3 Propuesta de Valor Única

**"Menos Papelería, Más Control"**

Diferenciadores clave:
- **Validación profesional:** Cada dato es verificado por un asesor contable antes de visualizarse
- **Seguridad garantizada:** Autenticación obligatoria con Gmail y cifrado de extremo a extremo
- **Simplicidad:** Solo 3 pasos para tener control financiero completo
- **Ecosistema Google:** Integración nativa con Forms, Sheets, Looker Studio
- **Especialización local:** Optimizado para normas y formatos venezolanos

### 1.4 Segmento de Mercado Objetivo

**Primario:**
- PYMES venezolanas con facturación mensual entre $5,000 - $100,000
- Sectores: comercio, servicios, manufactura ligera
- Uso de máquinas fiscales obligatorio
- 5-50 empleados
- Presencia física (tienda, oficina, local comercial)

**Secundario:**
- Profesionales independientes (médicos, abogados, consultores)
- Negocios en línea (e-commerce)
- Franquicias con múltiples locales
- Organizaciones sin fines de lucro

### 1.5 Modelo de Negocio

**SaaS (Software as a Service) con suscripción mensual**

**Planes:**

**Plan Básico - $29/mes**
- Hasta 100 transacciones mensuales
- 1 usuario (cliente)
- Validación estándar (48h)
- Dashboard básico
- Soporte por email

**Plan Profesional - $79/mes**
- Hasta 500 transacciones mensuales
- 3 usuarios (cliente + 2 colaboradores)
- Validación prioritaria (24h)
- Dashboard avanzado con Looker Studio
- Exportación de datos
- Soporte prioritario

**Plan Enterprise - $199/mes**
- Transacciones ilimitadas
- Usuarios ilimitados
- Validación en tiempo real (4h)
- Dashboard personalizado
- API access
- Integración con sistemas externos
- Soporte dedicado 24/7

**Ingresos Adicionales:**
- Servicios de consultoría contable
- Implementación personalizada
- Capacitación y entrenamiento
- Desarrollo de integraciones específicas

---

## 2. ARQUITECTURA TÉCNICA DETALLADA

### 2.1 Diagrama de Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAPA DE PRESENTACIÓN                     │
├─────────────────────────────────────────────────────────────────┤
│  Google Forms    │  Looker Studio  │  Gmail OAuth  │  Web App   │
│  (Captura)       │  (Visualización)│  (Auth)       │  (Gestión)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE PROCESAMIENTO                      │
├─────────────────────────────────────────────────────────────────┤
│  Google Document AI  │  Python Scripts  │  Cloud Functions     │
│  (OCR Avanzado)      │  (Normalización) │  (Automatización)    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CAPA DE ALMACENAMIENTO                     │
├─────────────────────────────────────────────────────────────────┤
│  Google Sheets      │  Google Drive    │  Cloud SQL            │
│  (Datos estructurados)│  (Archivos)      │  (Base de datos)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE INFRAESTRUCTURA                      │
├─────────────────────────────────────────────────────────────────┤
│  Google Cloud Run    │  Cloud Storage  │  Secret Manager         │
│  (Computing)         │  (Archivos)     │  (Seguridad)           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes Técnicos Detallados

#### 2.2.1 Google Forms (Captura de Datos)

**Configuración del Formulario:**

**Sección 1: Información del Cliente**
- Campo: RIF (validación de formato J-XXXXXXXX-X, V-XXXXXXXX-X, E-XXXXXXXX-X, G-XXXXXXXX-X)
- Campo: Nombre/Razón Social (texto, obligatorio)
- Campo: Sector (dropdown: Comercio, Servicios, Manufactura, Otros)
- Campo: Período fiscal (selector de mes/año)
- Campo: Observaciones (textarea, opcional)

**Sección 2: Carga de Archivos**
- Campo: Reportes Z (múltiples archivos, máximo 10MB cada uno)
- Campo: Facturas de ventas (múltiples archivos)
- Campo: Facturas de compras (múltiples archivos)
- Campo: Bases de datos (Excel, CSV, TXT)
- Campo: Otros documentos (PDF, imágenes)

**Validaciones del Formulario:**
- Validación de formato de RIF en tiempo real
- Límite de tamaño de archivo (10MB)
- Tipos de archivo aceptados (JPG, PNG, PDF, XLSX, XLS, CSV, TXT)
- Campos obligatorios marcados con asterisco
- Validación de período fiscal (no futuro)
- Detección de archivos duplicados

**Integración con Google Apps Script:**
```javascript
// Ejemplo conceptual de trigger al enviar formulario
function onFormSubmit(e) {
  const formData = e.response;
  const files = formData.getItemResponses();
  
  // Procesar cada archivo
  files.forEach(file => {
    if (file.getItem().getType() === FormApp.ItemType.FILE_UPLOAD) {
      processUploadedFile(file.getResponse());
    }
  });
  
  // Iniciar workflow de procesamiento
  startProcessingWorkflow(formData);
}
```

#### 2.2.2 Google Drive (Almacenamiento de Archivos)

**Estructura de Directorios:**

```
/
├── Clients/
│   ├── [RIF_CLIENTE_1]/
│   │   ├── Originals/
│   │   │   ├── Reportes_Z/
│   │   │   ├── Facturas_Ventas/
│   │   │   ├── Facturas_Compras/
│   │   │   └── Bases_Datos/
│   │   ├── Processed/
│   │   │   ├── OCR_Results/
│   │   │   ├── Normalized_Data/
│   │   │   └── Validated_Data/
│   │   └── Archive/
│   │       └── [AÑO]/
│   │           └── [MES]/
│   └── [RIF_CLIENTE_2]/
│       └── ...
├── Templates/
│   ├── Report_Z_Template.xlsx
│   └── Invoice_Template.pdf
└── Logs/
    ├── Processing_Logs/
    └── Error_Logs/
```

**Permisos de Acceso:**
- Cliente: Solo lectura de sus propios archivos
- Asesor: Lectura/escritura de archivos de sus clientes asignados
- Sistema: Escritura en todas las carpetas (procesamiento automático)
- Administrador: Acceso completo

**Versionado de Archivos:**
- Google Drive mantiene versiones automáticamente
- Política de retención: 7 años (cumplimiento fiscal)
- Archivo automático después de 1 año de inactividad

#### 2.2.3 Google Sheets (Base de Datos Centralizada)

**Estructura de Hojas de Cálculo:**

**Hoja 1: Clients (Información de Clientes)**
```
| Columna | Tipo | Descripción |
|---------|------|-------------|
| Client_ID | Text | Identificador único |
| RIF | Text | RIF del cliente |
| Name | Text | Nombre/Razón Social |
| Email | Text | Email de contacto |
| Sector | Dropdown | Sector de actividad |
| Plan | Dropdown | Plan de suscripción |
| Status | Dropdown | Activo, Inactivo, Pendiente |
| Created_Date | Date | Fecha de registro |
| Assigned_Advisor | Text | Asesor asignado |
| Last_Activity | Date | Última actividad |
```

**Hoja 2: Transactions (Transacciones)**
```
| Columna | Tipo | Descripción |
|---------|------|-------------|
| Transaction_ID | Text | Identificador único |
| Client_ID | Text | ID del cliente |
| Date | Date | Fecha de transacción |
| Type | Dropdown | Venta, Compra, Gasto |
| Amount | Number | Monto |
| Tax_Amount | Number | Monto de impuesto |
| Tax_Rate | Number | Tasa impositiva |
| Description | Text | Descripción |
| Category | Dropdown | Categoría |
| Status | Dropdown | Pendiente, Validado, Rechazado |
| Source_File | Text | Archivo origen |
| Extracted_Data | JSON | Datos extraídos por OCR |
| Validation_Notes | Text | Notas del asesor |
| Validated_By | Text | Asesor que validó |
| Validation_Date | Date | Fecha de validación |
```

**Hoja 3: Documents (Metadatos de Documentos)**
```
| Columna | Tipo | Descripción |
|---------|------|-------------|
| Document_ID | Text | Identificador único |
| Client_ID | Text | ID del cliente |
| File_Name | Text | Nombre del archivo |
| File_Type | Dropdown | PDF, JPG, XLSX, CSV |
| Document_Type | Dropdown | Reporte Z, Factura, Base de datos |
| Upload_Date | Date | Fecha de carga |
| File_Size | Number | Tamaño en bytes |
| File_Path | Text | Ruta en Google Drive |
| Processing_Status | Dropdown | Pendiente, Procesando, Completado, Error |
| OCR_Confidence | Number | Confianza del OCR (0-1) |
| Extraction_Date | Date | Fecha de extracción |
```

**Hoja 4: Validation_Log (Historial de Validaciones)**
```
| Columna | Tipo | Descripción |
|---------|------|-------------|
| Log_ID | Text | Identificador único |
| Transaction_ID | Text | ID de transacción |
| Validator_ID | Text | ID del asesor |
| Action | Dropdown | Aprobado, Rechazado, Observación |
| Notes | Text | Notas de validación |
| Timestamp | DateTime | Fecha y hora |
| Previous_Status | Dropdown | Estado anterior |
| New_Status | Dropdown | Nuevo estado |
```

**Hoja 5: Dashboard_Data (Datos para Looker Studio)**
```
| Columna | Tipo | Descripción |
|---------|------|-------------|
| Date | Date | Fecha |
| Client_ID | Text | ID del cliente |
| Revenue | Number | Ingresos |
| Expenses | Number | Egresos |
| Net_Income | Number | Ingreso neto |
| Tax_Collected | Number | Impuesto cobrado |
| Tax_Paid | Number | Impuesto pagado |
| Transaction_Count | Number | Cantidad de transacciones |
| Category | Text | Categoría |
```

#### 2.2.4 Google Document AI (OCR Especializado)

**Configuración de Document AI:**

**Procesadores Especializados:**

1. **Form Parser** para formularios estructurados
   - Extracción de campos específicos
   - Reconocimiento de checkboxes
   - Tablas y listas

2. **Invoice Parser** para facturas
   - Extracción de número de factura
   - Identificación de RIF emisor
   - Montos y tasas impositivas
   - Fechas de emisión y vencimiento

3. **OCR Engine** para documentos no estructurados
   - Reconocimiento de texto general
   - Soporte para múltiples idiomas (español)
   - Manejo de imágenes de baja calidad

**Flujo de Procesamiento OCR:**

```
Archivo Cargado → Clasificación de Tipo → Procesador Adecuado → Extracción de Datos → Validación de Campos → Normalización → Almacenamiento
```

**Mejoras para Contexto Venezolano:**

- **Entrenamiento personalizado:**
  - Modelos entrenados con facturas venezolanas
  - Reconocimiento de formatos SENIAT
  - Identificación de códigos de impuestos locales

- **Diccionarios personalizados:**
  - Lista de bancos venezolanos
  - Códigos de actividad económica
  - Terminología fiscal venezolana

- **Validación de formato:**
  - Verificación de formato de RIF
  - Validación de montos en bolívares/dólares
  - Detección de reportes Z específicos

#### 2.2.5 Looker Studio (Dashboard Interactivo)

**Configuración de Dashboards:**

**Dashboard 1: Resumen Ejecutivo**

**Componentes:**
- **Tarjeta 1:** Ingresos Totales del Mes (con indicador de variación vs mes anterior)
- **Tarjeta 2:** Egresos Totales del Mes (con indicador de variación vs mes anterior)
- **Tarjeta 3:** Ingreso Neto (con indicador de variación vs mes anterior)
- **Tarjeta 4:** Margen de Beneficio (porcentaje)
- **Gráfico 1:** Evolución de Ingresos (línea, últimos 12 meses)
- **Gráfico 2:** Distribución de Egresos por Categoría (circular)
- **Gráfico 3:** Comparación Ingresos vs Egresos (barra apilada)

**Dashboard 2: Análisis Detallado**

**Componentes:**
- **Gráfico 1:** Ingresos por Día (línea, mes actual)
- **Gráfico 2:** Top 10 Productos/Servicios (barra horizontal)
- **Gráfico 3:** Ingresos por Cliente (barra)
- **Gráfico 4:** Tendencia de Gastos (línea, últimos 6 meses)
- **Tabla 1:** Transacciones Detalladas (con filtros y búsqueda)

**Dashboard 3: Análisis Comparativo**

**Componentes:**
- **Gráfico 1:** Comparación Mensual (barra agrupada: actual vs anterior)
- **Gráfico 2:** Comparación Anual (línea: 2024 vs 2025)
- **Gráfico 3:** Cumplimiento de Presupuesto (gauge)
- **Gráfico 4:** Benchmark vs Industria (barra)

**Filtros Globales:**
- Selector de período (mes, trimestre, año)
- Selector de categoría
- Selector de cliente (para asesores con múltiples clientes)
- Botón de actualización en tiempo real

#### 2.2.6 Google Cloud Functions (Automatización)

**Funciones Principales:**

**Function 1: process_uploaded_file**
```python
# Concepto de función
def process_uploaded_file(event, context):
    """
    Trigger cuando se carga un archivo a Cloud Storage
    """
    file_data = event
    client_id = extract_client_id(file_data['name'])
    
    # Clasificar tipo de documento
    doc_type = classify_document(file_data)
    
    # Enviar a Document AI apropiado
    if doc_type == 'invoice':
        result = process_with_invoice_parser(file_data)
    elif doc_type == 'report_z':
        result = process_with_form_parser(file_data)
    
    # Guardar resultado en Sheets
    save_to_sheets(result, client_id)
    
    # Notificar asesor
    notify_advisor(client_id, result)
```

**Function 2: validate_transaction**
```python
# Concepto de función
def validate_transaction(request):
    """
    Endpoint para que el asesor valide transacciones
    """
    transaction_id = request.json['transaction_id']
    validator_id = request.json['validator_id']
    action = request.json['action']  # approve, reject, observe
    notes = request.json.get('notes', '')
    
    # Actualizar estado en Sheets
    update_transaction_status(transaction_id, action, validator_id, notes)
    
    # Si aprobado, actualizar dashboard
    if action == 'approve':
        update_dashboard_data(transaction_id)
    
    # Notificar cliente
    notify_client(transaction_id, action)
    
    return {'status': 'success'}
```

**Function 3: generate_monthly_report**
```python
# Concepto de función
def generate_monthly_report(event, context):
    """
    Trigger mensual para generar reportes
    """
    # Ejecutar el último día de cada mes
    for client in get_all_active_clients():
        report = generate_report(client['id'], month, year)
        save_report_to_drive(report, client['id'])
        send_report_email(client['email'], report)
```

#### 2.2.7 Gmail OAuth (Autenticación)

**Flujo de Autenticación OAuth 2.0:**

```
Usuario → Click "Iniciar Sesión con Gmail" 
→ Redirección a Google OAuth
→ Usuario autoriza acceso
→ Google devuelve authorization code
→ Sistema intercambia code por access token
→ Sistema obtiene refresh token
→ Sesión establecida
→ Acceso a recursos de Google
```

**Permisos Solicitados (Scopes):**
- `https://www.googleapis.com/auth/userinfo.email` - Email del usuario
- `https://www.googleapis.com/auth/userinfo.profile` - Información básica del perfil
- `https://www.googleapis.com/auth/drive.readonly` - Acceso a Drive (lectura)
- `https://www.googleapis.com/auth/spreadsheets` - Acceso a Sheets
- `https://www.googleapis.com/auth/forms` - Acceso a Forms

**Gestión de Tokens:**
- Access token: Expira en 1 hora
- Refresh token: No expira (salvo revocación)
- Almacenamiento seguro en Secret Manager
- Rotación automática de tokens

---

## 3. MODELOS DE DATOS Y ESQUEMAS

### 3.1 Esquema de Base de Datos Relacional (Cloud SQL)

**Tabla: clients**
```sql
CREATE TABLE clients (
    client_id VARCHAR(36) PRIMARY KEY,
    rif VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    sector ENUM('comercio', 'servicios', 'manufactura', 'otros'),
    plan ENUM('basico', 'profesional', 'enterprise'),
    status ENUM('active', 'inactive', 'pending', 'suspended'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    assigned_advisor_id VARCHAR(36),
    google_drive_folder_id VARCHAR(255),
    INDEX idx_rif (rif),
    INDEX idx_status (status),
    INDEX idx_advisor (assigned_advisor_id),
    FOREIGN KEY (assigned_advisor_id) REFERENCES users(user_id)
);
```

**Tabla: users**
```sql
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role ENUM('client', 'advisor', 'admin'),
    google_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);
```

**Tabla: documents**
```sql
CREATE TABLE documents (
    document_id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type ENUM('pdf', 'jpg', 'png', 'xlsx', 'xls', 'csv', 'txt'),
    document_type ENUM('report_z', 'invoice_sale', 'invoice_purchase', 'database', 'other'),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size BIGINT,
    google_drive_file_id VARCHAR(255),
    processing_status ENUM('pending', 'processing', 'completed', 'error'),
    ocr_confidence DECIMAL(3,2),
    extraction_date TIMESTAMP,
    error_message TEXT,
    INDEX idx_client (client_id),
    INDEX idx_status (processing_status),
    INDEX idx_date (upload_date),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
```

**Tabla: transactions**
```sql
CREATE TABLE transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    document_id VARCHAR(36),
    transaction_date DATE NOT NULL,
    type ENUM('sale', 'purchase', 'expense'),
    amount DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2),
    tax_rate DECIMAL(5,2),
    description TEXT,
    category VARCHAR(100),
    status ENUM('pending', 'validated', 'rejected'),
    extracted_data JSON,
    validation_notes TEXT,
    validated_by VARCHAR(36),
    validation_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_client (client_id),
    INDEX idx_date (transaction_date),
    INDEX idx_status (status),
    INDEX idx_type (type),
    FOREIGN KEY (client_id) REFERENCES clients(client_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id),
    FOREIGN KEY (validated_by) REFERENCES users(user_id)
);
```

**Tabla: validation_log**
```sql
CREATE TABLE validation_log (
    log_id VARCHAR(36) PRIMARY KEY,
    transaction_id VARCHAR(36) NOT NULL,
    validator_id VARCHAR(36) NOT NULL,
    action ENUM('approved', 'rejected', 'observed'),
    notes TEXT,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_transaction (transaction_id),
    INDEX idx_validator (validator_id),
    INDEX idx_date (created_at),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (validator_id) REFERENCES users(user_id)
);
```

**Tabla: subscriptions**
```sql
CREATE TABLE subscriptions (
    subscription_id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    plan ENUM('basico', 'profesional', 'enterprise'),
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('active', 'cancelled', 'expired', 'trial'),
    monthly_price DECIMAL(10,2),
    transaction_limit INT,
    users_limit INT,
    INDEX idx_client (client_id),
    INDEX idx_status (status),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
```

### 3.2 Esquema de Google Sheets (Alternativa)

**Hoja: Configuration**
```
| Key | Value | Description |
|-----|-------|-------------|
| API_Endpoint | https://api.pinad.com | URL base de API |
| Max_File_Size | 10485760 | Tamaño máximo en bytes |
| Supported_Formats | pdf,jpg,png,xlsx,xls,txt | Formatos aceptados |
| Tax_Rates | {"iva": 16, "islr": 34} | Tasas impositivas |
| Validation_Timeout | 48 | Horas para validación |
```

**Hoja: Categories**
```
| Category_ID | Category_Name | Parent_Category | Type |
|-------------|---------------|-----------------|------|
| CAT001 | Ventas de Productos | NULL | Ingreso |
| CAT002 | Servicios | NULL | Ingreso |
| CAT003 | Alquiler | NULL | Ingreso |
| CAT004 | Compras de Inventario | NULL | Egreso |
| CAT005 | Servicios Básicos | NULL | Egreso |
| CAT006 | Nómina | NULL | Egreso |
| CAT007 | Impuestos | NULL | Egreso |
```

---

## 4. INTEGRACIÓN CON GOOGLE ECOSYSTEM

### 4.1 Google Forms

**Implementación Detallada:**

**Configuración del Formulario:**

1. **Creación del Formulario:**
   - Usar Google Forms API o interfaz web
   - Configurar título: "(π)NAD - Carga de Documentos Contables"
   - Descripción: "Sistema de contabilidad automatizada. Sube tus documentos para procesamiento."

2. **Sección de Autenticación:**
   - Pregunta: "Email de Gmail (obligatorio para seguridad)"
   - Tipo: Validación de email
   - Mensaje de ayuda: "Usa tu cuenta de Gmail para garantizar cifrado de archivos"

3. **Sección de Información del Negocio:**
   - Pregunta 1: "RIF del Negocio"
     - Tipo: Texto corto
     - Validación: Expresión regular para formato venezolano
     - Regex: `^[JVEG]-\d{8}-\d$`
   
   - Pregunta 2: "Nombre/Razón Social"
     - Tipo: Texto corto
     - Obligatorio: Sí
   
   - Pregunta 3: "Sector de Actividad"
     - Tipo: Lista desplegable
     - Opciones: Comercio, Servicios, Manufactura, Otros
   
   - Pregunta 4: "Período Fiscal"
     - Tipo: Fecha (mes/año)
     - Validación: No permitir fechas futuras

4. **Sección de Carga de Archivos:**
   - Pregunta 1: "Reportes Z (Máquinas Fiscales)"
     - Tipo: Carga de archivos
     - Permitir múltiples archivos: Sí
     - Tipos aceptados: PDF, JPG, PNG
     - Límite de tamaño: 10MB por archivo
   
   - Pregunta 2: "Facturas de Ventas"
     - Tipo: Carga de archivos
     - Permitir múltiples archivos: Sí
     - Tipos aceptados: PDF, JPG, PNG
   
   - Pregunta 3: "Facturas de Compras"
     - Tipo: Carga de archivos
     - Permitir múltiples archivos: Sí
     - Tipos aceptados: PDF, JPG, PNG
   
   - Pregunta 4: "Bases de Datos"
     - Tipo: Carga de archivos
     - Tipos aceptados: XLSX, XLS, CSV, TXT
   
   - Pregunta 5: "Observaciones"
     - Tipo: Párrafo
     - Obligatorio: No

**Integración con Google Apps Script:**

```javascript
// Script de backend para Google Forms
const FORM_ID = 'FORM_ID_HERE';
const SHEETS_ID = 'SHEETS_ID_HERE';
const DRIVE_FOLDER_ID = 'DRIVE_FOLDER_ID_HERE';

function onFormSubmit(e) {
  const form = FormApp.openById(FORM_ID);
  const response = e.response;
  const itemResponses = response.getItemResponses();
  
  // Extraer datos del formulario
  const formData = {
    email: itemResponses[0].getResponse(),
    rif: itemResponses[1].getResponse(),
    name: itemResponses[2].getResponse(),
    sector: itemResponses[3].getResponse(),
    period: itemResponses[4].getResponse(),
    report_z_files: itemResponses[5].getResponse(),
    sales_invoices: itemResponses[6].getResponse(),
    purchase_invoices: itemResponses[7].getResponse(),
    databases: itemResponses[8].getResponse(),
    notes: itemResponses[9].getResponse()
  };
  
  // Crear carpeta para el cliente
  const clientFolder = createClientFolder(formData.rif, formData.name);
  
  // Procesar archivos
  processFiles(formData, clientFolder);
  
  // Guardar en Sheets
  saveToSheets(formData);
  
  // Enviar notificación
  sendNotification(formData.email, formData.rif);
}

function createClientFolder(rif, name) {
  const parentFolder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
  const folderName = `${rif} - ${name}`;
  const folder = parentFolder.createFolder(folderName);
  
  // Crear subcarpetas
  folder.createFolder('Originals');
  folder.createFolder('Processed');
  folder.createFolder('Validated');
  
  return folder;
}

function processFiles(formData, clientFolder) {
  const originalsFolder = clientFolder.getFoldersByName('Originals').next();
  
  // Procesar cada tipo de archivo
  const fileTypes = [
    { key: 'report_z_files', subfolder: 'Reportes_Z' },
    { key: 'sales_invoices', subfolder: 'Facturas_Ventas' },
    { key: 'purchase_invoices', subfolder: 'Facturas_Compras' },
    { key: 'databases', subfolder: 'Bases_Datos' }
  ];
  
  fileTypes.forEach(type => {
    if (formData[type.key]) {
      const subfolder = originalsFolder.createFolder(type.subfolder);
      formData[type.key].forEach(fileId => {
        const file = DriveApp.getFileById(fileId);
        file.makeCopy(file.getName(), subfolder);
      });
    }
  });
}

function saveToSheets(formData) {
  const sheets = SpreadsheetApp.openById(SHEETS_ID);
  const sheet = sheets.getSheetByName('Submissions');
  
  sheet.appendRow([
    new Date(),
    formData.email,
    formData.rif,
    formData.name,
    formData.sector,
    formData.period,
    formData.report_z_files ? formData.report_z_files.length : 0,
    formData.sales_invoices ? formData.sales_invoices.length : 0,
    formData.purchase_invoices ? formData.purchase_invoices.length : 0,
    formData.databases ? formData.databases.length : 0,
    'Pending',
    formData.notes
  ]);
}

function sendNotification(email, rif) {
  MailApp.sendEmail({
    to: email,
    subject: '(π)NAD - Documentos Recibidos',
    body: `Hemos recibido tus documentos para el RIF ${rif}. 
           El procesamiento tomará 24-48 horas. 
           Te notificaremos cuando estén listos para revisión.`
  });
}
```

### 4.2 Google Sheets

**Configuración de Hojas de Cálculo:**

**Hoja: Submissions (Registro de Envíos)**
```
| Timestamp | Email | RIF | Name | Sector | Period | Report_Z_Count | Sales_Count | Purchase_Count | DB_Count | Status | Notes |
|-----------|-------|-----|------|--------|--------|----------------|-------------|-----------------|----------|--------|-------|
```

**Hoja: Processing_Queue (Cola de Procesamiento)**
```
| Queue_ID | Submission_ID | File_ID | File_Type | Processing_Status | Priority | Created_At | Started_At | Completed_At | Error_Message |
|----------|---------------|---------|-----------|-------------------|----------|------------|------------|---------------|---------------|
```

**Hoja: OCR_Results (Resultados de OCR)**
```
| Result_ID | File_ID | Extracted_Data | Confidence | Processing_Time | Validated | Validation_Notes |
|-----------|---------|----------------|------------|-----------------|-----------|------------------|
```

**Hoja: Transactions (Transacciones Procesadas)**
```
| Transaction_ID | Client_ID | Date | Type | Amount | Tax_Amount | Category | Status | Validated_By |
|----------------|-----------|------|------|--------|------------|----------|--------|--------------|
```

**Fórmulas Automáticas:**

**En hoja Submissions:**
- Columna Status: Fórmula condicional basada en Processing_Queue
- Columna Total_Files: =SUM([@Report_Z_Count]:[@DB_Count])

**En hoja Dashboard_Data:**
- Columna Revenue: =SUMIFS(Transactions[Amount], Transactions[Type], "sale", Transactions[Date], DATE(YEAR(TODAY()), MONTH(TODAY()), 1))
- Columna Expenses: =SUMIFS(Transactions[Amount], Transactions[Type], "purchase", Transactions[Date], DATE(YEAR(TODAY()), MONTH(TODAY()), 1))
- Columna Net_Income: =[@Revenue]-[@Expenses]

### 4.3 Google Drive

**Organización de Archivos:**

**Estructura Jerárquica:**

```
(pinad_drive_root)/
├── 01_Clients/
│   ├── J-12345678-9_Empresa_ABC/
│   │   ├── 01_Originals/
│   │   │   ├── 2024/
│   │   │   │   ├── 01_Enero/
│   │   │   │   │   ├── Reportes_Z/
│   │   │   │   │   ├── Facturas_Ventas/
│   │   │   │   │   ├── Facturas_Compras/
│   │   │   │   │   └── Bases_Datos/
│   │   │   │   ├── 02_Febrero/
│   │   │   │   └── ...
│   │   │   └── 2025/
│   │   ├── 02_Processed/
│   │   │   ├── OCR_Results/
│   │   │   ├── Normalized_Data/
│   │   │   └── Extracted_Images/
│   │   ├── 03_Validated/
│   │   │   ├── Approved/
│   │   │   └── Rejected/
│   │   └── 04_Archive/
│   │       └── [AÑO]/
│   └── V-98765432-1_Empresa_XYZ/
│       └── ...
├── 02_Templates/
│   ├── Report_Z_Template.pdf
│   ├── Invoice_Template.pdf
│   └── Database_Template.xlsx
├── 03_Processing/
│   ├── Temp_Files/
│   └── Queue/
├── 04_Reports/
│   ├── Monthly_Reports/
│   └── Annual_Reports/
├── 05_Logs/
│   ├── Processing_Logs/
│   ├── Error_Logs/
│   └── Access_Logs/
└── 06_Configuration/
    ├── Tax_Rates.json
    ├── Categories.json
    └── Validation_Rules.json
```

**Permisos y Compartición:**

**Nivel de Carpeta:**
- **01_Clients/[CLIENTE]:**
  - Cliente: Editor (puede subir archivos)
  - Asesor asignado: Editor (puede procesar archivos)
  - Sistema: Propietario (acceso completo)

- **02_Templates:**
  - Todos los usuarios: Lector

- **03_Processing:**
  - Sistema: Propietario
  - Asesores: Editor

- **04_Reports:**
  - Cliente: Lector
  - Asesor: Editor

- **05_Logs:**
  - Administradores: Lector

**API de Drive para Gestión:**

```javascript
// Ejemplo de uso de Drive API
function createClientFolder(clientData) {
  const driveService = getDriveService();
  
  // Crear carpeta principal del cliente
  const folderMetadata = {
    'name': `${clientData.rif}_${clientData.name}`,
    'parents': ['CLIENTS_FOLDER_ID'],
    'mimeType': 'application/vnd.google-apps.folder'
  };
  
  const folder = driveService.files.create({
    resource: folderMetadata,
    fields: 'id'
  });
  
  // Crear subcarpetas
  const subfolders = ['Originals', 'Processed', 'Validated', 'Archive'];
  subfolders.forEach(subfolderName => {
    const subfolderMetadata = {
      'name': subfolderName,
      'parents': [folder.id],
      'mimeType': 'application/vnd.google-apps.folder'
    };
    driveService.files.create({
      resource: subfolderMetadata
    });
  });
  
  // Compartir con cliente
  driveService.permissions.create({
    'fileId': folder.id,
    'resource': {
      'role': 'writer',
      'type': 'user',
      'emailAddress': clientData.email
    }
  });
  
  return folder.id;
}
```

### 4.4 Looker Studio

**Configuración de Data Sources:**

**Data Source 1: Google Sheets (Transactions)**
- Conexión: Google Sheets API
- Hoja: Transactions
- Refresco: Cada 15 minutos
- Caché: 5 minutos

**Data Source 2: Google Sheets (Dashboard_Data)**
- Conexión: Google Sheets API
- Hoja: Dashboard_Data
- Refresco: Cada hora
- Caché: 30 minutos

**Configuración de Dashboards:**

**Dashboard Principal:**

**Página 1: Resumen Ejecutivo**
- **Tarjeta 1:** Ingresos Totales
  - Métrica: SUM(Revenue)
  - Comparación: vs mes anterior
  - Formato: Moneda ($)
  - Color: Verde (positivo), Rojo (negativo)

- **Tarjeta 2:** Egresos Totales
  - Métrica: SUM(Expenses)
  - Comparación: vs mes anterior
  - Formato: Moneda ($)
  - Color: Verde (menor), Rojo (mayor)

- **Tarjeta 3:** Ingreso Neto
  - Métrica: SUM(Revenue) - SUM(Expenses)
  - Comparación: vs mes anterior
  - Formato: Moneda ($)
  - Color: Verde (positivo), Rojo (negativo)

- **Gráfico 1:** Evolución de Ingresos
  - Tipo: Línea de tiempo
  - Dimensión: Date
  - Métrica: Revenue
  - Período: Últimos 12 meses
  - Tendencia: Línea de tendencia

- **Gráfico 2:** Distribución de Egresos
  - Tipo: Circular
  - Dimensión: Category
  - Métrica: Expenses
  - Etiquetas: Porcentaje

- **Gráfico 3:** Comparación Ingresos vs Egresos
  - Tipo: Barra apilada
  - Dimensión: Date (mes)
  - Métricas: Revenue, Expenses
  - Período: Últimos 6 meses

**Página 2: Análisis Detallado**
- **Gráfico 1:** Ingresos por Día
  - Tipo: Línea
  - Dimensión: Date (día)
  - Métrica: Revenue
  - Filtro: Mes actual

- **Gráfico 2:** Top Productos/Servicios
  - Tipo: Barra horizontal
  - Dimensión: Category
  - Métrica: Revenue
  - Top: 10

- **Tabla 1:** Transacciones Detalladas
  - Columnas: Date, Type, Amount, Category, Description
  - Filtros: Tipo, Categoría, Rango de fechas
  - Búsqueda: Texto completo
  - Exportación: CSV, Excel

**Página 3: Comparativas**
- **Gráfico 1:** Comparación Mensual
  - Tipo: Barra agrupada
  - Dimensión: Date (mes)
  - Métricas: Revenue (actual), Revenue (año anterior)
  - Período: Últimos 12 meses

- **Gráfico 2:** Tendencia Anual
  - Tipo: Línea compuesta
  - Dimensión: Date (mes)
  - Métricas: Revenue 2024, Revenue 2025
  - Período: Año completo

- **Gráfico 3:** Benchmark
  - Tipo: Barra
  - Dimensión: Métrica
  - Métricas: Tu negocio, Promedio industria
  - Datos: Cargados manualmente o desde API externa

### 4.5 Google Document AI

**Configuración de Procesadores:**

**Procesador 1: Invoice Parser (Facturas)**
```json
{
  "processor_id": "invoice-parser",
  "location": "us",
  "features": {
    "extraction": {
      "fields": [
        "invoice_number",
        "invoice_date",
        "due_date",
        "vendor_name",
        "vendor_rif",
        "total_amount",
        "tax_amount",
        "tax_rate",
        "line_items",
        "payment_terms"
      ]
    },
    "classification": {
      "document_types": ["invoice", "receipt", "credit_note"]
    }
  },
  "custom_models": {
    "venezuelan_invoices": {
      "training_data": "path/to/training/data",
      "accuracy_target": 0.95
    }
  }
}
```

**Procesador 2: Form Parser (Formularios)**
```json
{
  "processor_id": "form-parser",
  "location": "us",
  "features": {
    "extraction": {
      "fields": [
        "form_type",
        "report_date",
        "report_number",
        "total_sales",
        "total_tax",
        "cash_sales",
        "credit_sales",
        "returns"
      ]
    },
    "table_extraction": {
      "enabled": true,
      "header_detection": true
    }
  }
}
```

**Flujo de Procesamiento:**

```
1. Archivo cargado a Cloud Storage
2. Trigger invoca Cloud Function
3. Cloud Function clasifica tipo de documento
4. Envía a Document AI apropiado
5. Document AI procesa y extrae datos
6. Resultados validados y normalizados
7. Datos guardados en Sheets/Cloud SQL
8. Notificación enviada al asesor
```

**Mejoras para Contexto Venezolano:**

**Diccionario de Entidades:**
```json
{
  "rif_patterns": [
    "^[J]-\\d{8}-\\d$",
    "^[V]-\\d{8}-\\d$",
    "^[E]-\\d{8}-\\d$",
    "^[G]-\\d{8}-\\d$"
  ],
  "currency_symbols": ["$", "Bs.", "BsS"],
  "tax_codes": ["IVA", "ISLR", "MUNICIPAL"],
  "document_types": ["FACTURA", "NOTA DE CRÉDITO", "NOTA DE DÉBITO", "REPORTE Z"],
  "venezuelan_banks": ["BANCO DE VENEZUELA", "BANESCO", "MERCANTIL", "PROVINCIAL"]
}
```

---

## 5. PROCESOS DE NEGOCIO DETALLADOS

### 5.1 Proceso de Onboarding de Cliente

**Paso 1: Registro Inicial**
- Cliente accede a landing page
- Click en "Comenzar Gratis"
- Redirección a Google OAuth
- Cliente autoriza acceso con Gmail
- Sistema crea cuenta en base de datos
- Cliente completar perfil (RIF, nombre, sector)

**Paso 2: Verificación de RIF**
- Sistema valida formato de RIF
- Sistema consulta SENIAT (si API disponible)
- Sistema verifica que RIF no esté duplicado
- Cliente confirma información

**Paso 3: Selección de Plan**
- Cliente ve comparación de planes
- Cliente selecciona plan (prueba gratuita 14 días)
- Sistema configura suscripción

**Paso 4: Configuración Inicial**
- Sistema crea carpeta en Google Drive
- Sistema envía email de bienvenida
- Sistema asigna asesor (automático o manual)
- Sistema programa primera sesión de onboarding

**Paso 5: Capacitación**
- Asesor contacta al cliente
- Sesión de demostración (30 min)
- Explicación del flujo de 3 pasos
- Resolución de dudas iniciales
- Cliente listo para usar el sistema

### 5.2 Proceso de Carga de Documentos

**Paso 1: Preparación de Documentos**
- Cliente reúne documentos del período
- Cliente verifica calidad de imágenes
- Cliente organiza archivos por tipo

**Paso 2: Acceso al Formulario**
- Cliente recibe enlace único (URL con token)
- Cliente inicia sesión con Gmail
- Sistema verifica sesión activa
- Sistema carga formulario pre-completado

**Paso 3: Completar Información**
- Cliente verifica RIF y nombre
- Cliente selecciona período fiscal
- Cliente agrega observaciones (opcional)

**Paso 4: Carga de Archivos**
- Cliente arrastra archivos al formulario
- Sistema valida tipo y tamaño
- Sistema muestra previsualización
- Cliente confirma carga

**Paso 5: Confirmación**
- Sistema muestra resumen de carga
- Cliente confirma envío
- Sistema genera ticket de carga
- Sistema envía notificación de recepción

### 5.3 Proceso de Procesamiento de Documentos

**Paso 1: Recepción y Clasificación**
- Sistema recibe notificación de carga
- Sistema descarga archivos de Google Forms
- Sistema clasifica tipo de cada archivo
- Sistema asigna prioridad de procesamiento

**Paso 2: Extracción de Datos (OCR)**
- Sistema envía archivos a Document AI
- Document AI procesa cada archivo
- Sistema recibe datos extraídos
- Sistema evalúa confianza de extracción

**Paso 3: Normalización**
- Sistema normaliza formatos de fecha
- Sistema normaliza montos (decimales)
- Sistema unifica códigos de impuestos
- Sistema limpia caracteres especiales

**Paso 4: Validación Automática**
- Sistema verifica integridad de datos
- Sistema detecta anomalías obvias
- Sistema valida rangos de montos
- Sistema marca datos sospechosos

**Paso 5: Almacenamiento**
- Sistema guarda datos en Sheets
- Sistema guarda archivos en Drive
- Sistema crea registro en log
- Sistema actualiza estado de procesamiento

### 5.4 Proceso de Validación Profesional

**Paso 1: Notificación al Asesor**
- Sistema envía alerta al asesor
- Sistema muestra resumen de carga
- Sistema indica prioridad (según plan)

**Paso 2: Revisión Preliminar**
- Asesor accede a interfaz de validación
- Asesor visualiza archivos originales
- Asesor compara datos extraídos
- Asesor identifica problemas

**Paso 3: Validación Detallada**
- Asesor verifica montos vs reportes Z
- Asesor valida fechas y períodos
- Asesor confirma cálculos de impuestos
- Asesor verifica clasificación

**Paso 4: Toma de Decisión**
- Asesor aprueba datos correctos
- Asesor solicita corrección si hay errores
- Asesor agrega notas explicativas
- Asesor documenta decisión

**Paso 5: Notificación al Cliente**
- Sistema notifica estado al cliente
- Si aprobado: Dashboard actualizado
- Si corrección: Instrucciones específicas
- Si rechazado: Explicación del problema

### 5.5 Proceso de Visualización y Análisis

**Paso 1: Acceso al Dashboard**
- Cliente inicia sesión con Gmail
- Sistema verifica permisos
- Sistema carga dashboard personalizado
- Sistema muestra datos actualizados

**Paso 2: Exploración de Datos**
- Cliente navega entre páginas del dashboard
- Cliente aplica filtros y segmentaciones
- Cliente explora gráficos interactivos
- Cliente descarga reportes

**Paso 3: Análisis Comparativo**
- Cliente compara períodos
- Cliente analiza tendencias
- Cliente identifica patrones
- Cliente toma decisiones informadas

**Paso 4: Exportación y Compartición**
- Cliente exporta datos a Excel
- Cliente genera reportes PDF
- Cliente comparte con equipo
- Cliente archiva para auditoría

---

## 6. CASOS DE USO Y ESCENARIOS

### 6.1 Caso de Uso 1: PYME de Comercio

**Perfil:**
- Tienda de ropa en Caracas
- 15 empleados
- Facturación mensual: $25,000
- Usa máquina fiscal obligatoria

**Escenario:**
1. **Registro:**
   - Dueño accede a (π)NAD
   - Se registra con Gmail
   - Completa perfil (RIF: J-12345678-9)
   - Selecciona plan Profesional

2. **Primera Carga:**
   - Dueño reúne reportes Z del mes
   - Escanea facturas de compras
   - Accede al formulario
   - Carga 15 reportes Z y 30 facturas

3. **Procesamiento:**
   - Sistema procesa archivos en 4 horas
   - OCR extrae datos con 95% de confianza
   - Datos normalizados y guardados

4. **Validación:**
   - Asesor revisa datos
   - Verifica conciliación de reportes Z
   - Aprueba 45 de 47 transacciones
   - Solicita corrección de 2 facturas

5. **Corrección:**
   - Dueño recibe notificación
   - Vuelve a cargar 2 facturas
   - Sistema reprocesa
   - Asesor aprueba

6. **Dashboard:**
   - Dueño accede a dashboard
   - Ve ingresos: $25,500
   - Ve egresos: $18,200
   - Ve ingreso neto: $7,300
   - Analiza tendencias mensuales

**Resultado:**
- Dueño ahorra 8 horas/mes en transcripción manual
- Tiene visibilidad en tiempo real
- Detecta anomalía en gasto de inventario
- Toma decisión de optimizar compras

### 6.2 Caso de Uso 2: Profesional Independiente

**Perfil:**
- Médico dermatólogo
- Consultorio propio
- 2 empleados
- Facturación mensual: $8,000

**Escenario:**
1. **Registro:**
   - Médico se registra con Gmail
   - Completa perfil (RIF: V-98765432-1)
   - Selecciona plan Básico

2. **Carga Mensual:**
   - Médico carga reportes Z
   - Carga facturas de compras (equipos, suministros)
   - Sistema procesa en 24 horas

3. **Validación:**
   - Asesor valida datos
   - Verifica deducciones fiscales
   - Aprueba todas las transacciones

4. **Dashboard:**
   - Médico ve ingresos por consulta
   - Ve gastos por categoría
   - Calcula margen de beneficio
   - Planifica inversiones

**Resultado:**
- Médico optimiza gastos operativos
- Identifica servicios más rentables
- Mejora planificación fiscal
- Aumenta margen en 15%

### 6.3 Caso de Uso 3: Franquicia con Múltiples Locales

**Perfil:**
- Franquicia de comida rápida
- 5 locales en Caracas
- 50 empleados
- Facturación mensual: $80,000

**Escenario:**
1. **Registro:**
   - Dueño se registra
   - Selecciona plan Enterprise
   - Configura múltiples usuarios

2. **Carga Consolidada:**
   - Cada local carga sus documentos
   - Sistema consolida datos
   - Asesor valida por local

3. **Dashboard Corporativo:**
   - Dueño ve consolidado de todos los locales
   - Compara rendimiento por local
   - Identifica local menos rentable
   - Toma decisiones de optimización

**Resultado:**
- Visibilidad consolidada en tiempo real
- Comparación de rendimiento entre locales
- Identificación de mejores prácticas
- Optimización de inventario centralizado

---

## 7. ROADMAP 2026-2027 DETALLADO

### 7.1 Fase 1: Inicio de Operaciones (Q1 2026)

**Objetivos:**
- Lanzamiento de MVP (Minimum Viable Product)
- Adquisición de primeros 50 clientes
- Validación del modelo de negocio

**Hitos:**
- **Mes 1:**
  - Desarrollo de Google Forms básico
  - Configuración de Google Sheets
  - Implementación de Gmail OAuth
  - Pruebas internas

- **Mes 2:**
  - Beta testing con 10 clientes piloto
  - Recolección de feedback
  - Ajustes y mejoras
  - Documentación inicial

- **Mes 3:**
  - Lanzamiento público
  - Campaña de marketing inicial
  - Adquisición de primeros 50 clientes
  - Soporte manual intensivo

**KPIs:**
- 50 clientes activos
- 80% tasa de retención
- 4.5/5 satisfacción del cliente
- 95% tasa de éxito de OCR

### 7.2 Fase 2: Digitalización y Visualización (Q2 2026)

**Objetivos:**
- Implementación completa de Google Forms
- Google Sheets como base de datos centralizada
- Looker Studio para dashboards

**Hitos:**
- **Mes 4:**
  - Google Forms optimizado con validaciones
  - Integración con Google Apps Script
  - Automatización de procesamiento

- **Mes 5:**
  - Google Sheets con estructura completa
  - Fórmulas automatizadas
  - Integración con Drive

- **Mes 6:**
  - Looker Studio configurado
  - Dashboards personalizados
  - Reportes automatizados

**KPIs:**
- 150 clientes activos
- 90% tasa de éxito de OCR
- 4.7/5 satisfacción del cliente
- 70% reducción de tiempo de procesamiento

### 7.3 Fase 3: Reportes con Looker Studio (Q3 2026)

**Objetivos:**
- Dashboards interactivos avanzados
- Análisis comparativo
- Exportación de reportes

**Hitos:**
- **Mes 7:**
  - Dashboards multi-página
  - Filtros dinámicos
  - Comparativas temporales

- **Mes 8:**
  - Benchmarks de industria
  - Análisis de tendencias
  - Alertas inteligentes

- **Mes 9:**
  - Exportación a múltiples formatos
  - Programación de reportes
  - Compartición segura

**KPIs:**
- 300 clientes activos
- 95% tasa de éxito de OCR
- 4.8/5 satisfacción del cliente
- 80% clientes usan dashboards semanalmente

### 7.4 Fase 4: Inteligencia para Normalización (Q4 2026)

**Objetivos:**
- Implementación de Vertas AUgamini
- Reconocimiento agnóstico de formatos
- Aprendizaje automático

**Hitos:**
- **Mes 10:**
  - Integración con Vertas AUgamini
  - Entrenamiento con datos venezolanos
  - Pruebas de precisión

- **Mes 11:**
  - Reconocimiento de múltiples formatos
  - Normalización automática
  - Reducción de validación manual

- **Mes 12:**
  - Modelo en producción
  - Monitoreo de precisión
  - Retrain continuo

**KPIs:**
- 500 clientes activos
- 98% tasa de éxito de OCR
- 50% reducción de validación manual
- 4.9/5 satisfacción del cliente

### 7.5 Fase 5: Integración de Google Document AI (Q1 2027)

**Objetivos:**
- OCR especializado para facturas venezolanas
- Extracción automática de datos
- Procesamiento en tiempo real

**Hitos:**
- **Mes 13:**
  - Configuración de Document AI
  - Entrenamiento de modelos personalizados
  - Diccionarios venezolanos

- **Mes 14:**
  - Procesador de facturas
  - Procesador de reportes Z
  - Validación de formatos SENIAT

- **Mes 15:**
  - Integración completa
  - Procesamiento en tiempo real
  - Reducción de tiempo a 4 horas

**KPIs:**
- 750 clientes activos
- 99% tasa de éxito de OCR
- 4 horas tiempo de procesamiento
- 4.9/5 satisfacción del cliente

### 7.6 Fase 6: Automatización con Python y SQL (Q2 2027)

**Objetivos:**
- Procesamiento con Python/Pandas
- Google Cloud SQL para base de datos
- Normalización de datos

**Hitos:**
- **Mes 16:**
  - Migración a Cloud SQL
  - Scripts de Python para procesamiento
  - Pipelines automatizados

- **Mes 17:**
  - Normalización con Pandas
  - Procesamiento de grandes volúmenes
  - Optimización de queries

- **Mes 18:**
  - Automatización completa
  - Monitoreo y alertas
  - Escalabilidad horizontal

**KPIs:**
- 1,000 clientes activos
- 99.5% tasa de éxito de OCR
- 2 horas tiempo de procesamiento
- Capacidad de 10,000 transacciones/día

### 7.7 Fase 7: Desarrollo Multiplataforma con Flutter (Q3 2027)

**Objetivos:**
- Aplicación móvil nativa
- Captura inteligente con cámara
- Sincronización offline

**Hitos:**
- **Mes 19:**
  - Desarrollo de app Flutter
  - Integración con cámara
  - Captura inteligente de documentos

- **Mes 20:**
  - Sincronización offline
  - Notificaciones push
  - Dashboard móvil

- **Mes 21:**
  - Despliegue en iOS y Android
  - Publicación en stores
  - Onboarding móvil

**KPIs:**
- 1,500 clientes activos
- 60% uso de app móvil
- 4.9/5 satisfacción del cliente
- 30% aumento en retención

### 7.8 Fase 8: Interfaz Dual (Q4 2027)

**Objetivos:**
- Portal móvil para cliente
- Panel maestro para profesional
- Separación de roles

**Hitos:**
- **Mes 22:**
  - Portal móvil cliente
  - Captura inteligente
  - Dashboard simplificado

- **Mes 23:**
  - Panel maestro asesor
  - Gestión de múltiples clientes
  - Herramientas de validación

- **Mes 24:**
  - Integración completa
  - Flujos de trabajo optimizados
  - Comunicación cliente-asesor

**KPIs:**
- 2,000 clientes activos
- 70% uso de app móvil
- 50 asesores activos
- 4.9/5 satisfacción del cliente

### 7.9 Fase 9: Project IDX y Desarrollo Cloud (Q1 2028)

**Objetivos:**
- Programación en la nube
- Optimización de rendimiento
- Facilidad de simulación

**Hitos:**
- **Mes 25:**
  - Migración a Google Cloud Run
  - Contenerización de servicios
  - CI/CD automatizado

- **Mes 26:**
  - Optimización de rendimiento
  - Balanceo de carga
  - Caching inteligente

- **Mes 27:**
  - Simulación de APP
  - Testing automatizado
  - Monitoreo avanzado

**KPIs:**
- 3,000 clientes activos
- 99.9% uptime
- <1 segundo tiempo de respuesta
- Escalabilidad a 10,000 clientes

### 7.10 Fase 10: Despliegue en Google Cloud Run (Q2 2028)

**Objetivos:**
- Despliegue completo en Cloud Run
- Auto-scaling
- Alta disponibilidad

**Hitos:**
- **Mes 28:**
  - Configuración de Cloud Run
  - Auto-scaling automático
  - Load balancing

- **Mes 29:**
  - Alta disponibilidad (99.9%)
  - Disaster recovery
  - Backups automatizados

- **Mes 30:**
  - Optimización de costos
  - Monitoreo de recursos
  - Alertas proactivas

**KPIs:**
- 5,000 clientes activos
- 99.9% uptime
- Costos optimizados
- Capacidad de 50,000 transacciones/día

### 7.11 Fase 11: Seguridad y Escalabilidad SaaS (Q3 2028)

**Objetivos:**
- Cifrado de extremo a extremo
- Arquitectura multi-inquilino
- Gestión de cientos de clientes

**Hitos:**
- **Mes 31:**
  - Cifrado E2E implementado
  - Gestión de claves con Secret Manager
  - Auditoría de seguridad

- **Mes 32:**
  - Arquitectura multi-inquilino
  - Aislamiento de datos por cliente
  - Gestión de permisos granular

- **Mes 33:**
  - Escalabilidad a cientos de clientes
  - Optimización de recursos
  - Monitoreo de capacidad

**KPIs:**
- 10,000 clientes activos
- 100% cumplimiento de seguridad
- Aislamiento de datos garantizado
- Capacidad de 100,000 transacciones/día

### 7.12 Fase 12: Hub de Integraciones y APIs (Q4 2028)

**Objetivos:**
- Conexión con sistemas externos
- API keys y webhooks
- Secret Manager

**Hitos:**
- **Mes 34:**
  - Desarrollo de API REST
  - Documentación de API
  - Portal de desarrolladores

- **Mes 35:**
  - Webhooks seguros
  - Integraciones con sistemas contables
  - Conexión con bancos

- **Mes 36:**
  - Hub de integraciones
  - Marketplace de integraciones
  - Soporte para desarrolladores

**KPIs:**
- 15,000 clientes activos
- 50 integraciones disponibles
- 1,000 desarrolladores registrados
- Ecosistema de integraciones activo

---

## 8. ARQUITECTURA DE SEGURIDAD

### 8.1 Autenticación y Autorización

**OAuth 2.0 con Google Identity:**

**Flujo Detallado:**
1. Usuario solicita acceso
2. Sistema redirige a Google OAuth
3. Usuario autoriza aplicación
4. Google devuelve authorization code
5. Sistema intercambia code por access token
6. Sistema obtiene refresh token
7. Tokens almacenados en Secret Manager
8. Sesión establecida con JWT

**Gestión de Sesiones:**
- Access token: 1 hora de validez
- Refresh token: 30 días de validez
- JWT: 24 horas de validez
- Sesión inactiva: 30 minutos timeout

**Roles y Permisos:**

**Rol: Cliente**
- Ver sus propios datos
- Cargar documentos
- Ver dashboard
- Exportar reportes

**Rol: Asesor**
- Ver datos de clientes asignados
- Validar transacciones
- Agregar notas de validación
- Ver dashboard de clientes

**Rol: Administrador**
- Acceso completo al sistema
- Gestionar usuarios
- Configurar sistema
- Ver logs y auditoría

### 8.2 Cifrado de Datos

**En Tránsito:**
- TLS 1.3 para todas las conexiones
- Certificados SSL válidos (Let's Encrypt)
- HSTS (HTTP Strict Transport Security)
- Perfect Forward Secrecy

**En Reposito:**
- Google Drive: AES-256
- Google Sheets: Cifrado automático
- Cloud SQL: AES-256
- Secret Manager: AES-256
- Cloud Storage: AES-256

**Cifrado de Archivos:**
- Archivos originales: Cifrado por Google
- Datos extraídos: Cifrado antes de almacenar
- Logs: Cifrado con rotación de claves
- Backups: Cifrado con claves separadas

### 8.3 Control de Acceso

**Por Cliente:**
- Aislamiento completo de datos
- Cada cliente tiene su propia carpeta en Drive
- Filtrado automático en todas las consultas
- Auditoría de accesos

**Por Rol:**
- RBAC (Role-Based Access Control)
- Permisos granulares por recurso
- Herencia de permisos
- Revocación inmediata

**Por Recurso:**
- Archivos originales: Cliente + Asesor
- Datos procesados: Cliente (lectura), Asesor (escritura)
- Dashboard: Solo cliente
- Logs: Solo administrador

### 8.4 Auditoría y Compliance

**Logs de Auditoría:**
- Todos los accesos registrados
- Todas las modificaciones registradas
- Timestamps en UTC
- Retención: 7 años

**Alertas de Seguridad:**
- Intentos de acceso fallidos
- Accesos desde ubicaciones inusuales
- Actividad voluminosa sospechosa
- Cambios en permisos

**Compliance:**
- GDPR (si aplica)
- CCPA (si aplica)
- Ley de Protección de Datos Personales (Venezuela)
- Normas SENIAT

---

## 9. ESTRATEGIA DE IMPLEMENTACIÓN

### 9.1 Fase de Pre-Lanzamiento

**Mes 1-2: Preparación**
- Desarrollo de MVP
- Pruebas internas
- Documentación
- Configuración de infraestructura

**Mes 3: Beta Testing**
- 10 clientes piloto
- Recolección de feedback
- Ajustes y mejoras
- Preparación de soporte

### 9.2 Fase de Lanzamiento

**Mes 4: Lanzamiento Público**
- Campaña de marketing
- Adquisición de primeros 50 clientes
- Soporte intensivo
- Monitoreo continuo

**Mes 5-6: Optimización**
- Análisis de métricas
- Mejoras basadas en feedback
- Optimización de procesos
- Escalabilidad

### 9.3 Fase de Crecimiento

**Mes 7-12: Expansión**
- Implementación de nuevas features
- Adquisición de 500 clientes
- Expansión del equipo
- Optimización de costos

### 9.4 Fase de Madurez

**Año 2: Consolidación**
- 2,000 clientes activos
- Ecosistema estable
- Integraciones avanzadas
- Expansión a otros mercados

---

## 10. CUMPLIMIENTO NORMATIVO

### 10.1 Normas Venezolanas

**SENIAT:**
- Retención de documentos: 7 años
- Formatos de facturación electrónicos
- Reportes Z obligatorios
- Declaraciones mensuales

**SENCAMER:**
- Normas de calidad para software
- Certificación de sistemas
- Estándares de seguridad

**Ley Especial contra Delitos Informáticos:**
- Protección de datos
- Delitos informáticos
- Penalizaciones

### 10.2 Normas Internacionales

**GDPR (Europa):**
- Consentimiento explícito
- Derecho al olvido
- Portabilidad de datos
- Notificación de brechas

**CCPA (California):**
- Opt-out de venta de datos
- Derecho a saber
- Derecho a eliminar
- No discriminación

### 10.3 Certificaciones

**ISO 27001:** Seguridad de información
**SOC 2:** Seguridad, disponibilidad, integridad
**PCI DSS:** Si se procesa pagos

---

## 11. MÉTRICAS Y KPIs

### 11.1 KPIs Operativos

**Procesamiento:**
- Tiempo promedio de procesamiento: < 24 horas
- Tasa de éxito de OCR: > 95%
- Porcentaje de validación manual: < 20%
- Tiempo de respuesta del sistema: < 1 segundo

**Calidad:**
- Precisión de extracción de datos: > 95%
- Tasa de errores de clasificación: < 5%
- Satisfacción del cliente: > 4.5/5
- Tasa de retención: > 80%

### 11.2 KPIs de Negocio

**Crecimiento:**
- Nuevos clientes por mes: 50+
- Tasa de churn: < 5%
- CAC (Costo de Adquisición de Cliente): <$50
- LTV (Lifetime Value): >$500

**Ingresos:**
- MRR (Monthly Recurring Revenue): Crecimiento 20% mensual
- ARPU (Average Revenue Per User): >$50
- Margen bruto: > 70%
- CAC/LTV ratio: < 0.1

### 11.3 KPIs de Producto

**Adopción:**
- DAU (Daily Active Users): > 60% de clientes
- MAU (Monthly Active Users): > 90% de clientes
- Feature adoption rate: > 70%
- Time to value: < 7 días

**Engagement:**
- Sesiones promedio por usuario: 10/mes
- Tiempo promedio en dashboard: 15 minutos
- Tasa de exportación de reportes: > 50%
- Tasa de uso de dashboards: > 80%

---

## 12. ANÁLISIS DE COMPETENCIA

### 12.1 Competidores Directos

**Contador en Línea:**
- Fortalezas: Establecido en mercado
- Debilidades: Sin automatización, proceso manual
- Oportunidad: Automatización con IA

**Facturación Web:**
- Fortalezas: Especializado en facturación
- Debilidades: Sin análisis financiero
- Oportunidad: Dashboards avanzados

### 12.2 Competidores Indirectos

**Excel:**
- Fortalezas: Universal, flexible
- Debilidades: Manual, propenso a errores
- Oportunidad: Automatización y validación

**Software contable tradicional:**
- Fortalezas: Completo, establecido
- Debilidades: Costoso, complejo, requiere instalación
- Oportunidad: SaaS, accesible, fácil de usar

### 12.3 Ventaja Competitiva

**Únicas:**
- Validación profesional por asesor
- Especialización en mercado venezolano
- Integración nativa con Google ecosystem
- Proceso de 3 pasos simple

**Diferenciadores:**
- OCR especializado para documentos venezolanos
- Dashboards interactivos en tiempo real
- Seguridad con Gmail OAuth
- Modelo SaaS accesible

---

## CONCLUSIÓN

Esta documentación completa cubre todos los aspectos técnicos, de negocio y estratégicos del sistema (π)NAD. Desde la arquitectura técnica detallada hasta el roadmap de implementación 2026-2027, proporciona una base sólida para el desarrollo y expansión del sistema.

El enfoque en simplicidad (3 pasos), seguridad (Gmail OAuth) y especialización local (Venezuela) posiciona a (π)NAD como una solución única en el mercado, capaz de transformar la gestión contable de PYMEs venezolanas y expandirse posteriormente a otros mercados latinoamericanos.
