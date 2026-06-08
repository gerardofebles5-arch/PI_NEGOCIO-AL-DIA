# GUÍA DE IMPLEMENTACIÓN TÉCNICA - Sistema (π)NAD

## ÍNDICE

1. [Visión General de Implementación](#1-visión-general-de-implementación)
2. [Requisitos Previos](#2-requisitos-previos)
3. [Configuración de Google Cloud Project](#3-configuración-de-google-cloud-project)
4. [Implementación de Google Forms](#4-implementación-de-google-forms)
5. [Implementación de Google Sheets](#5-implementación-de-google-sheets)
6. [Implementación de Google Drive](#6-implementación-de-google-drive)
7. [Implementación de Google Document AI](#7-implementación-de-google-document-ai)
8. [Implementación de Looker Studio](#8-implementación-de-looker-studio)
9. [Implementación de Google Cloud Functions](#9-implementación-de-google-cloud-functions)
10. [Implementación de Gmail OAuth](#10-implementación-de-gmail-oauth)
11. [Despliegue en Google Cloud Run](#11-despliegue-en-google-cloud-run)
12. [Configuración de Base de Datos](#12-configuración-de-base-de-datos)
13. [Implementación de Webhooks](#13-implementación-de-webhooks)
14. [Testing y QA](#14-testing-y-qa)
15. [Monitoreo y Logging](#15-monitoreo-y-logging)
16. [Seguridad y Compliance](#16-seguridad-y-compliance)

---

## 1. VISIÓN GENERAL DE IMPLEMENTACIÓN

### 1.1 Arquitectura de Implementación

La implementación de (π)NAD sigue una arquitectura serverless basada en Google Cloud Platform, utilizando servicios gestionados para minimizar la complejidad operativa.

**Componentes Principales:**
- Google Forms: Captura de datos
- Google Sheets: Base de datos centralizada
- Google Drive: Almacenamiento de archivos
- Google Document AI: OCR especializado
- Looker Studio: Visualización de datos
- Google Cloud Functions: Automatización
- Gmail OAuth: Autenticación
- Google Cloud Run: Computing
- Cloud SQL: Base de datos relacional

### 1.2 Estrategia de Implementación

**Fase 1: MVP (Mínimo Producto Viable)**
- Google Forms básico
- Google Sheets manual
- Procesamiento OCR manual
- Looker Studio básico

**Fase 2: Automatización**
- Google Apps Script
- Document AI básico
- Cloud Functions
- Automatización de workflows

**Fase 3: Escalabilidad**
- Cloud SQL
- Cloud Run
- API REST
- Webhooks

**Fase 4: Avanzado**
- Document AI personalizado
- Looker Studio avanzado
- Multi-tenant
- Integraciones

### 1.3 Stack Tecnológico

**Frontend:**
- Google Forms (no-code)
- Looker Studio (no-code)
- Web App (opcional, React/Vue)

**Backend:**
- Google Apps Script
- Python (Cloud Functions)
- Node.js (opcional)

**Base de Datos:**
- Google Sheets (inicial)
- Cloud SQL (escalabilidad)

**OCR:**
- Google Document AI
- EasyOCR (backup)

**Infraestructura:**
- Google Cloud Platform
- Cloud Run
- Cloud Storage
- Secret Manager

---

## 2. REQUISITOS PREVIOS

### 2.1 Cuentas y Permisos

**Google Cloud Project:**
- Cuenta de Google Cloud
- Proyecto creado en GCP
- Facturación habilitada
- Roles necesarios:
  - Project Owner
  - Service Account Admin
  - Cloud Functions Developer
  - Cloud Run Admin

**Google Workspace (Opcional):**
- Dominio de Google Workspace
- Acceso administrativo
- Configuración de OAuth

### 2.2 Herramientas de Desarrollo

**Requeridas:**
- Google Cloud SDK (gcloud)
- Python 3.11+
- Node.js 18+ (opcional)
- Git
- Docker (opcional)

**Opcionales:**
- VS Code
- Postman (para testing de API)
- Terraform (para IaC)

### 2.3 APIs de Google Habilitadas

**Lista de APIs a habilitar:**
```
gcloud services enable \
  cloudbuild.googleapis.com \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  drive.googleapis.com \
  sheets.googleapis.com \
  forms.googleapis.com \
  docs.googleapis.com \
  documentai.googleapis.com \
  looker.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### 2.4 Variables de Entorno

**Archivo .env:**
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=pinad-production
GOOGLE_CLOUD_REGION=us-central1

# Google Drive
DRIVE_FOLDER_ID=folder_id_here

# Google Sheets
SHEETS_ID=sheets_id_here

# Document AI
DOCUMENT_AI_LOCATION=us
DOCUMENT_AI_PROCESSOR_ID=processor_id_here

# OAuth
OAUTH_CLIENT_ID=client_id_here
OAUTH_CLIENT_SECRET=client_secret_here
OAUTH_REDIRECT_URI=https://app.pinad.com/callback

# Database
CLOUD_SQL_CONNECTION_NAME=connection_name_here
DB_USER=pinad_user
DB_PASSWORD=secure_password_here
DB_NAME=pinad_db

# Secret Manager
SECRET_MANAGER_PROJECT=pinad-production

# API
API_BASE_URL=https://api.pinad.com/v1
API_KEY=api_key_here
```

---

## 3. CONFIGURACIÓN DE GOOGLE CLOUD PROJECT

### 3.1 Creación del Proyecto

```bash
# Crear proyecto
gcloud projects create pinad-production \
  --name="PINAD Production"

# Establecer proyecto actual
gcloud config set project pinad-production

# Habilitar facturación
# (Se hace en consola de Google Cloud)
```

### 3.2 Creación de Service Accounts

```bash
# Crear service account para Cloud Functions
gcloud iam service-accounts create pinad-functions \
  --display-name="PINAD Cloud Functions"

# Crear service account para Cloud Run
gcloud iam service-accounts create pinad-run \
  --display-name="PINAD Cloud Run"

# Crear service account para Document AI
gcloud iam service-accounts create pinad-documentai \
  --display-name="PINAD Document AI"
```

### 3.3 Asignación de Roles

```bash
# Asignar roles a service accounts
gcloud projects add-iam-policy-binding pinad-production \
  --member="serviceAccount:pinad-functions@pinad-production.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"

gcloud projects add-iam-policy-binding pinad-production \
  --member="serviceAccount:pinad-functions@pinad-production.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding pinad-production \
  --member="serviceAccount:pinad-functions@pinad-production.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding pinad-production \
  --member="serviceAccount:pinad-functions@pinad-production.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### 3.4 Creación de Claves de Service Account

```bash
# Crear clave JSON (solo para desarrollo local)
gcloud iam service-accounts keys create pinad-functions-key.json \
  --iam-account=pinad-functions@pinad-production.iam.gserviceaccount.com

# Exportar variable de entorno
export GOOGLE_APPLICATION_CREDENTIALS="./pinad-functions-key.json"
```

---

## 4. IMPLEMENTACIÓN DE GOOGLE FORMS

### 4.1 Creación del Formulario

**Método 1: Interfaz Web**
1. Acceder a forms.google.com
2. Click en "Blank"
3. Configurar título: "(π)NAD - Carga de Documentos"
4. Añadir preguntas según especificación

**Método 2: Google Forms API**
```python
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Autenticación
SCOPES = ['https://www.googleapis.com/auth/forms.body']
creds = service_account.Credentials.from_service_account_file(
    'pinad-functions-key.json',
    scopes=SCOPES
)
forms_service = build('forms', 'v1', credentials=creds)

# Crear formulario
NEW_FORM = {
    "info": {
        "title": "(π)NAD - Carga de Documentos",
        "document_title": "(π)NAD - Carga de Documentos"
    }
}

form = forms_service.forms().create(body=NEW_FORM).execute()
form_id = form['formId']
print(f"Formulario creado con ID: {form_id}")
```

### 4.2 Configuración de Preguntas

```python
# Añadir pregunta de email
EMAIL_QUESTION = {
    "requests": [{
        "createItem": {
            "item": {
                "title": "Email de Gmail (obligatorio para seguridad)",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {
                            "paragraph": False
                        }
                    }
                }
            },
            "location": {"index": 0}
        }
    }]
}

forms_service.forms().batchUpdate(
    formId=form_id,
    body=EMAIL_QUESTION
).execute()

# Añadir pregunta de RIF
RIF_QUESTION = {
    "requests": [{
        "createItem": {
            "item": {
                "title": "RIF del Negocio",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {
                            "paragraph": False
                        }
                    }
                }
            },
            "location": {"index": 1}
        }
    }]
}

forms_service.forms().batchUpdate(
    formId=form_id,
    body=RIF_QUESTION
).execute()
```

### 4.3 Configuración de Validación

```python
# Validación de RIF con regex
RIF_VALIDATION = {
    "requests": [{
        "updateItem": {
            "item": {
                "title": "RIF del Negocio",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {
                            "paragraph": False
                        },
                        "validation": {
                            "regex": {
                                "pattern": "^[JVEG]-\\d{8}-\\d$"
                            }
                        }
                    }
                }
            },
            "location": {"index": 1},
            "updateMask": "questionItem.question.validation"
        }
    }]
}

forms_service.forms().batchUpdate(
    formId=form_id,
    body=RIF_VALIDATION
).execute()
```

### 4.4 Configuración de Carga de Archivos

```python
# Pregunta de carga de archivos
FILE_UPLOAD_QUESTION = {
    "requests": [{
        "createItem": {
            "item": {
                "title": "Reportes Z (Máquinas Fiscales)",
                "questionItem": {
                    "question": {
                        "required": False,
                        "fileUploadQuestion": {
                            "type": "ANY",
                            "maxFiles": 10,
                            "maxFileSize": 10485760  # 10MB
                        }
                    }
                }
            },
            "location": {"index": 5}
        }
    }]
}

forms_service.forms().batchUpdate(
    formId=form_id,
    body=FILE_UPLOAD_QUESTION
).execute()
```

### 4.5 Integración con Google Apps Script

```javascript
// Script de backend para Google Forms
const FORM_ID = 'FORM_ID_HERE';
const SHEETS_ID = 'SHEETS_ID_HERE';
const DRIVE_FOLDER_ID = 'DRIVE_FOLDER_ID_HERE';

function onFormSubmit(e) {
  const form = FormApp.openById(FORM_ID);
  const response = e.response;
  const itemResponses = response.getItemResponses();
  
  // Extraer datos
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
  
  // Crear carpeta del cliente
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

---

## 5. IMPLEMENTACIÓN DE GOOGLE SHEETS

### 5.1 Creación de Hoja de Cálculo

```python
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(
    'pinad-functions-key.json',
    scopes=SCOPES
)
sheets_service = build('sheets', 'v4', credentials=creds)

# Crear hoja de cálculo
SPREADSHEET_BODY = {
    'properties': {
        'title': 'PINAD - Base de Datos Centralizada'
    }
}

spreadsheet = sheets_service.spreadsheets().create(
    body=SPREADSHEET_BODY
).execute()

spreadsheet_id = spreadsheet['spreadsheetId']
print(f"Hoja de cálculo creada con ID: {spreadsheet_id}")
```

### 5.2 Creación de Hojas (Tabs)

```python
# Crear hoja de Clients
REQUEST_BODY = {
    'requests': [{
        'addSheet': {
            'properties': {
                'title': 'Clients',
                'gridProperties': {
                    'rowCount': 1000,
                    'columnCount': 26
                }
            }
        }
    }]
}

sheets_service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body=REQUEST_BODY
).execute()

# Crear hoja de Transactions
REQUEST_BODY = {
    'requests': [{
        'addSheet': {
            'properties': {
                'title': 'Transactions',
                'gridProperties': {
                    'rowCount': 10000,
                    'columnCount': 20
                }
            }
        }
    }]
}

sheets_service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body=REQUEST_BODY
).execute()
```

### 5.3 Configuración de Encabezados

```python
# Configurar encabezados de Clients
HEADER_RANGE = 'Clients!A1:J1'
HEADER_VALUES = [
    ['Client_ID', 'RIF', 'Name', 'Email', 'Phone', 'Sector', 
     'Plan', 'Status', 'Created_Date', 'Assigned_Advisor']
]

sheets_service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range=HEADER_RANGE,
    valueInputOption='RAW',
    body={'values': HEADER_VALUES}
).execute()

# Configurar encabezados de Transactions
HEADER_RANGE = 'Transactions!A1:L1'
HEADER_VALUES = [
    ['Transaction_ID', 'Client_ID', 'Date', 'Type', 'Amount', 
     'Tax_Amount', 'Tax_Rate', 'Description', 'Category', 
     'Status', 'Validated_By', 'Validation_Date']
]

sheets_service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range=HEADER_RANGE,
    valueInputOption='RAW',
    body={'values': HEADER_VALUES}
).execute()
```

### 5.4 Formato de Celdas

```python
# Formato de fecha
DATE_FORMAT_REQUEST = {
    'requests': [{
        'repeatCell': {
            'range': {
                'sheetId': 1,  # Transactions sheet
                'startRowIndex': 1,
                'endRowIndex': 10000,
                'startColumnIndex': 2,  # Date column
                'endColumnIndex': 3
            },
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {
                        'type': 'DATE',
                        'pattern': 'yyyy-mm-dd'
                    }
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
        }
    }]
}

sheets_service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body=DATE_FORMAT_REQUEST
).execute()

# Formato de moneda
CURRENCY_FORMAT_REQUEST = {
    'requests': [{
        'repeatCell': {
            'range': {
                'sheetId': 1,
                'startRowIndex': 1,
                'endRowIndex': 10000,
                'startColumnIndex': 4,  # Amount column
                'endColumnIndex': 7  # Amount, Tax_Amount, Tax_Rate
            },
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {
                        'type': 'CURRENCY',
                        'pattern': '$#,##0.00'
                    }
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
        }
    }]
}

sheets_service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body=CURRENCY_FORMAT_REQUEST
).execute()
```

### 5.5 Protección de Hojas

```python
# Proteger hoja de Clients (solo lectura para usuarios)
PROTECTION_REQUEST = {
    'requests': [{
        'addProtectedRange': {
            'protectedRange': {
                'range': {
                    'sheetId': 0,  # Clients sheet
                },
                'description': 'Clients sheet - Read only',
                'warningOnly': False,
                'editors': {
                    'users': ['pinad-functions@pinad-production.iam.gserviceaccount.com']
                }
            }
        }
    }]
}

sheets_service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body=PROTECTION_REQUEST
).execute()
```

---

## 6. IMPLEMENTACIÓN DE GOOGLE DRIVE

### 6.1 Creación de Estructura de Carpetas

```python
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(
    'pinad-functions-key.json',
    scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=creds)

# Crear carpeta raíz
ROOT_FOLDER_METADATA = {
    'name': 'PINAD',
    'mimeType': 'application/vnd.google-apps.folder'
}

root_folder = drive_service.files().create(
    body=ROOT_FOLDER_METADATA,
    fields='id'
).execute()

root_folder_id = root_folder['id']
print(f"Carpeta raíz creada con ID: {root_folder_id}")

# Crear subcarpetas principales
SUBFOLDERS = [
    '01_Clients',
    '02_Templates',
    '03_Processing',
    '04_Reports',
    '05_Logs',
    '06_Configuration'
]

for folder_name in SUBFOLDERS:
    folder_metadata = {
        'name': folder_name,
        'parents': [root_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()
    print(f"Subcarpeta {folder_name} creada con ID: {folder['id']}")
```

### 6.2 Creación de Carpeta de Cliente

```python
def create_client_folder(client_data):
    """Crear estructura de carpetas para un cliente"""
    
    # Obtener carpeta de clients
    clients_folder = drive_service.files().list(
        q="name='01_Clients' and mimeType='application/vnd.google-apps.folder'",
        fields='files(id)'
    ).execute()
    
    clients_folder_id = clients_folder['files'][0]['id']
    
    # Crear carpeta del cliente
    client_folder_metadata = {
        'name': f"{client_data['rif']} - {client_data['name']}",
        'parents': [clients_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    client_folder = drive_service.files().create(
        body=client_folder_metadata,
        fields='id'
    ).execute()
    
    client_folder_id = client_folder['id']
    
    # Crear subcarpetas del cliente
    subfolders = ['Originals', 'Processed', 'Validated', 'Archive']
    
    for subfolder_name in subfolders:
        subfolder_metadata = {
            'name': subfolder_name,
            'parents': [client_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        drive_service.files().create(
            body=subfolder_metadata
        ).execute()
    
    # Compartir con cliente
    permission_metadata = {
        'role': 'writer',
        'type': 'user',
        'emailAddress': client_data['email']
    }
    
    drive_service.permissions().create(
        fileId=client_folder_id,
        body=permission_metadata,
        fields='id'
    ).execute()
    
    return client_folder_id
```

### 6.3 Compartición de Archivos

```python
def share_file_with_advisor(file_id, advisor_email):
    """Compartir archivo con asesor"""
    
    permission_metadata = {
        'role': 'writer',
        'type': 'user',
        'emailAddress': advisor_email
    }
    
    permission = drive_service.permissions().create(
        fileId=file_id,
        body=permission_metadata,
        fields='id'
    ).execute()
    
    return permission['id']
```

---

## 7. IMPLEMENTACIÓN DE GOOGLE DOCUMENT AI

### 7.1 Creación de Procesador

```python
from google.cloud import documentai

# Configuración
PROJECT_ID = "pinad-production"
LOCATION = "us"
PROCESSOR_DISPLAY_NAME = "PINAD Invoice Parser"
PROCESSOR_TYPE = "INVOICE_PROCESSOR"

# Crear cliente
client = documentai.DocumentProcessorServiceClient()

# Configurar procesador
processor = {
    "display_name": PROCESSOR_DISPLAY_NAME,
    "type_": PROCESSOR_TYPE,
}

# Crear procesador
parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
response = client.create_processor(parent=parent, processor=processor)

processor_id = response.name.split("/")[-1]
print(f"Procesador creado con ID: {processor_id}")
```

### 7.2 Procesamiento de Documento

```python
def process_document(file_path, processor_id):
    """Procesar documento con Document AI"""
    
    # Leer archivo
    with open(file_path, "rb") as image_file:
        image_content = image_file.read()
    
    # Crear request
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{processor_id}"
    
    raw_document = documentai.RawDocument(
        content=image_content,
        mime_type="application/pdf"
    )
    
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document
    )
    
    # Procesar
    result = client.process_document(request=request)
    
    # Extraer datos
    document = result.document
    
    extracted_data = {
        "text": document.text,
        "entities": []
    }
    
    for entity in document.entities:
        extracted_data["entities"].append({
            "type": entity.type_,
            "mention_text": entity.mention_text,
            "confidence": entity.confidence
        })
    
    return extracted_data
```

### 7.3 Entrenamiento Personalizado

```python
def train_custom_processor(training_data_path):
    """Entrenar procesador personalizado"""
    
    # Subir datos de entrenamiento
    # (Implementación específica según Document AI)
    
    # Configurar entrenamiento
    training_config = {
        "training_documents": training_data_path,
        "target_accuracy": 0.95
    }
    
    # Iniciar entrenamiento
    # (Implementación específica según Document AI)
    
    pass
```

---

## 8. IMPLEMENTACIÓN DE LOOKER STUDIO

### 8.1 Configuración de Data Source

**Método: Interfaz Web**
1. Acceder a lookerstudio.google.com
2. Click en "Create" > "Data Source"
3. Seleccionar "Google Sheets"
4. Autorizar acceso
5. Seleccionar hoja de cálculo
6. Configurar refresco (cada 15 minutos)

### 8.2 Creación de Dashboard

**Método: Interfaz Web**
1. Click en "Create" > "Report"
2. Seleccionar data source
3. Añadir gráficos:
   - Tarjetas de KPIs
   - Gráficos de línea
   - Gráficos circulares
   - Tablas
4. Configurar filtros
5. Personalizar diseño

### 8.3 Configuración de Filtros Globales

```javascript
// Script para configurar filtros en Looker Studio
// (Se hace principalmente en interfaz web)
```

---

## 9. IMPLEMENTACIÓN DE GOOGLE CLOUD FUNCTIONS

### 9.1 Creación de Cloud Function

```python
# main.py
import os
import json
from google.cloud import storage, documentai, secretmanager

def process_uploaded_file(event, context):
    """
    Cloud Function trigger cuando se carga un archivo
    """
    
    # Extraer información del evento
    file_data = event
    bucket_name = file_data['bucket']
    file_name = file_data['name']
    
    # Extraer client_id del nombre del archivo
    client_id = extract_client_id(file_name)
    
    # Clasificar tipo de documento
    doc_type = classify_document(file_name)
    
    # Procesar con Document AI
    if doc_type == 'invoice':
        result = process_with_invoice_parser(bucket_name, file_name)
    elif doc_type == 'report_z':
        result = process_with_form_parser(bucket_name, file_name)
    
    # Guardar resultado en Sheets
    save_to_sheets(result, client_id)
    
    # Notificar asesor
    notify_advisor(client_id, result)
    
    return {'status': 'success'}

def extract_client_id(file_name):
    """Extraer client_id del nombre del archivo"""
    # Implementación específica
    pass

def classify_document(file_name):
    """Clasificar tipo de documento"""
    # Implementación específica
    pass

def process_with_invoice_parser(bucket_name, file_name):
    """Procesar con parser de facturas"""
    # Implementación específica
    pass

def process_with_form_parser(bucket_name, file_name):
    """Procesar con parser de formularios"""
    # Implementación específica
    pass

def save_to_sheets(result, client_id):
    """Guardar resultado en Google Sheets"""
    # Implementación específica
    pass

def notify_advisor(client_id, result):
    """Notificar asesor"""
    # Implementación específica
    pass
```

### 9.2 Despliegue de Cloud Function

```bash
# Desplegar función
gcloud functions deploy process_uploaded_file \
  --runtime python311 \
  --trigger-resource pinad-uploads \
  --trigger-event google.storage.object.finalize \
  --region us-central1 \
  --service-account pinad-functions@pinad-production.iam.gserviceaccount.com \
  --entry-point process_uploaded_file \
  --memory 512MB \
  --timeout 540s
```

### 9.3 Configuración de Variables de Entorno

```bash
# Establecer variables de entorno
gcloud functions deploy process_uploaded_file \
  --set-env-vars SHEETS_ID=sheets_id_here \
  --set-env-vars DOCUMENT_AI_PROCESSOR_ID=processor_id_here \
  --set-env-vars SECRET_MANAGER_PROJECT=pinad-production
```

---

## 10. IMPLEMENTACIÓN DE GMAIL OAUTH

### 10.1 Configuración de OAuth 2.0

**En Google Cloud Console:**
1. Ir a APIs & Services > Credentials
2. Click en "Create Credentials" > "OAuth client ID"
3. Seleccionar "Web application"
4. Configurar:
   - Name: PINAD OAuth
   - Authorized redirect URIs: https://app.pinad.com/callback
5. Click en "Create"
6. Copiar Client ID y Client Secret

### 10.2 Implementación de Flujo OAuth

```python
from flask import Flask, redirect, request, session
from google.oauth2 import flow
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'https://app.pinad.com/callback'

@app.route('/login')
def login():
    """Iniciar flujo OAuth"""
    
    # Crear flujo OAuth
    oauth_flow = flow.Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=['https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=REDIRECT_URI
    )
    
    # Generar state para seguridad
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    
    # Generar URL de autorización
    authorization_url, state = oauth_flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=state
    )
    
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """Callback de OAuth"""
    
    # Verificar state
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return 'Error: Invalid state', 400
    
    # Crear flujo OAuth
    oauth_flow = flow.Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=['https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=REDIRECT_URI,
        state=state
    )
    
    # Intercambiar authorization code por tokens
    authorization_response = request.url
    oauth_flow.fetch_token(authorization_response=authorization_response)
    
    # Guardar credenciales en sesión
    credentials = oauth_flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Obtener información del usuario
    userinfo = get_userinfo(credentials.token)
    session['user_email'] = userinfo['email']
    
    return redirect('/dashboard')

def get_userinfo(access_token):
    """Obtener información del usuario"""
    import requests
    
    response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    return response.json()
```

---

## 11. DESPLIEGUE EN GOOGLE CLOUD RUN

### 11.1 Creación de Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
```

### 11.2 Creación de requirements.txt

```
Flask==3.0.0
google-cloud-storage==2.13.0
google-cloud-documentai==2.20.0
google-cloud-secret-manager==2.18.0
google-auth==2.23.4
google-api-python-client==2.108.0
gunicorn==21.2.0
```

### 11.3 Construcción de Imagen Docker

```bash
# Construir imagen
gcloud builds submit --tag gcr.io/pinad-production/pinad-app:latest .

# O usando Docker local
docker build -t pinad-app:latest .
docker tag pinad-app:latest gcr.io/pinad-production/pinad-app:latest
docker push gcr.io/pinad-production/pinad-app:latest
```

### 11.4 Despliegue en Cloud Run

```bash
# Desplegar
gcloud run deploy pinad-app \
  --image gcr.io/pinad-production/pinad-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account pinad-run@pinad-production.iam.gserviceaccount.com \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 100 \
  --min-instances 0 \
  --port 8080
```

### 11.5 Configuración de Variables de Entorno

```bash
# Establecer variables de entorno
gcloud run services update pinad-app \
  --region us-central1 \
  --set-env-vars SHEETS_ID=sheets_id_here \
  --set-env-vars DOCUMENT_AI_PROCESSOR_ID=processor_id_here \
  --set-env-vars OAUTH_CLIENT_ID=client_id_here \
  --set-env-vars OAUTH_CLIENT_SECRET=client_secret_here
```

---

## 12. CONFIGURACIÓN DE BASE DE DATOS

### 12.1 Creación de Instancia Cloud SQL

```bash
# Crear instancia
gcloud sql instances create pinad-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-auto-increase \
  --storage-size=10GB \
  --backup-start-time=03:00
```

### 12.2 Creación de Base de Datos

```bash
# Crear base de datos
gcloud sql databases create pinad_db \
  --instance=pinad-db
```

### 12.3 Creación de Usuario

```bash
# Crear usuario
gcloud sql users create pinad_user \
  --instance=pinad-db \
  --password=secure_password_here
```

### 12.4 Ejecución de Migraciones

```python
# migrations.py
import psycopg2
from google.cloud import secretmanager

def get_db_connection():
    """Obtener conexión a base de datos"""
    
    # Obtener credenciales de Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    secret_name = "projects/pinad-production/secrets/db-credentials/versions/latest"
    response = client.access_secret_version(name=secret_name)
    credentials = json.loads(response.payload.data.decode('utf-8'))
    
    # Conectar a base de datos
    conn = psycopg2.connect(
        host=credentials['host'],
        database=credentials['database'],
        user=credentials['user'],
        password=credentials['password']
    )
    
    return conn

def run_migrations():
    """Ejecutar migraciones"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla de clients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id VARCHAR(36) PRIMARY KEY,
            rif VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            sector VARCHAR(50),
            plan VARCHAR(20),
            status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_advisor_id VARCHAR(36)
        )
    """)
    
    # Crear tabla de transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id VARCHAR(36) PRIMARY KEY,
            client_id VARCHAR(36) NOT NULL,
            transaction_date DATE NOT NULL,
            type VARCHAR(20),
            amount DECIMAL(15,2) NOT NULL,
            tax_amount DECIMAL(15,2),
            description TEXT,
            category VARCHAR(100),
            status VARCHAR(20),
            validated_by VARCHAR(36),
            validation_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
```

---

## 13. IMPLEMENTACIÓN DE WEBHOOKS

### 13.1 Creación de Endpoint de Webhook

```python
# app.py
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = 'your_webhook_secret'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint de webhook"""
    
    # Verificar firma
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.get_data()
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return 'Invalid signature', 401
    
    # Procesar evento
    event = request.json
    event_type = event.get('event')
    data = event.get('data')
    
    if event_type == 'document.processed':
        handle_document_processed(data)
    elif event_type == 'transaction.validated':
        handle_transaction_validated(data)
    
    return jsonify({'status': 'received'}), 200

def handle_document_processed(data):
    """Manejar evento de documento procesado"""
    # Implementación específica
    pass

def handle_transaction_validated(data):
    """Manejar evento de transacción validada"""
    # Implementación específica
    pass
```

### 13.2 Envío de Webhooks

```python
import requests
import hmac
import hashlib

def send_webhook(webhook_url, event_type, data, secret):
    """Enviar webhook"""
    
    payload = {
        'event': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    
    # Generar firma
    signature = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Enviar
    response = requests.post(
        webhook_url,
        json=payload,
        headers={
            'X-Webhook-Signature': signature,
            'Content-Type': 'application/json'
        }
    )
    
    return response.status_code
```

---

## 14. TESTING Y QA

### 14.1 Pruebas Unitarias

```python
# test_app.py
import unittest
from app import process_uploaded_file

class TestCloudFunction(unittest.TestCase):
    
    def test_extract_client_id(self):
        """Probar extracción de client_id"""
        file_name = "J-12345678-9_Empresa_ABC_reporte_z.pdf"
        client_id = extract_client_id(file_name)
        self.assertEqual(client_id, "J-12345678-9")
    
    def test_classify_document(self):
        """Probar clasificación de documento"""
        file_name = "factura_001.pdf"
        doc_type = classify_document(file_name)
        self.assertEqual(doc_type, "invoice")
    
    def test_process_invoice(self):
        """Probar procesamiento de factura"""
        # Implementación específica
        pass

if __name__ == '__main__':
    unittest.main()
```

### 14.2 Pruebas de Integración

```python
# test_integration.py
import unittest
from google.cloud import storage

class TestIntegration(unittest.TestCase):
    
    def test_upload_and_process(self):
        """Probar carga y procesamiento completo"""
        # Subir archivo a Cloud Storage
        # Verificar que Cloud Function se ejecuta
        # Verificar que datos se guardan en Sheets
        pass
    
    def test_oauth_flow(self):
        """Probar flujo OAuth"""
        # Simular flujo OAuth completo
        pass

if __name__ == '__main__':
    unittest.main()
```

### 14.3 Pruebas de Carga

```python
# test_load.py
import locust
from locust import HttpUser, task, between

class PINADUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        """Al iniciar usuario"""
        # Login
        self.client.post("/login", json={"email": "test@example.com"})
    
    @task
    def upload_document(self):
        """Subir documento"""
        files = {'file': open('test.pdf', 'rb')}
        self.client.post("/documents", files=files)
    
    @task
    def get_dashboard(self):
        """Obtener dashboard"""
        self.client.get("/dashboard")
```

---

## 15. MONITOREO Y LOGGING

### 15.1 Configuración de Cloud Logging

```python
import logging
from google.cloud import logging

# Configurar logging client
logging_client = logging.Client()
logging_client.setup_logging()

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler de Cloud Logging
cloud_handler = logging_client.handler('pinad-cloud-functions')
cloud_handler.setLevel(logging.INFO)
logger.addHandler(cloud_handler)
```

### 15.2 Configuración de Cloud Monitoring

```python
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()

def create_custom_metric():
    """Crear métrica personalizada"""
    
    project_name = f"projects/{PROJECT_ID}"
    
    descriptor = monitoring_v3.MetricDescriptor(
        name=f"{project_name}/metricDescriptors/custom.documents_processed",
        description="Number of documents processed",
        display_name="Documents Processed",
        metric_kind=monitoring_v3.MetricDescriptor.MetricKind.CUMULATIVE,
        value_type=monitoring_v3.MetricDescriptor.ValueType.INT64,
    )
    
    client.create_metric_descriptor(name=project_name, metric_descriptor=descriptor)
```

### 15.3 Configuración de Alertas

```bash
# Crear política de alertas
gcloud alpha monitoring policies create \
  --display-name="High Error Rate" \
  --condition="resource.type=\"cloud_function\" AND resource.labels.function_name=\"process_uploaded_file\" AND metric.type=\"logging.googleapis.com/user/count\" AND severity=\"ERROR\"" \
  --notification-channels=[EMAIL_CHANNEL_ID]
```

---

## 16. SEGURIDAD Y COMPLIANCE

### 16.1 Gestión de Secretos con Secret Manager

```python
from google.cloud import secretmanager

def store_secret(secret_id, secret_value):
    """Almacenar secreto"""
    
    client = secretmanager.SecretManagerServiceClient()
    
    parent = f"projects/{PROJECT_ID}"
    secret = {"replication": {"automatic": {}}}
    
    response = client.create_secret(
        parent=parent,
        secret_id=secret_id,
        secret=secret
    )
    
    # Añadir versión del secreto
    parent = f"projects/{PROJECT_ID}/secrets/{secret_id}"
    payload = secret_value.encode('UTF-8')
    
    client.add_secret_version(
        parent=parent,
        payload={"data": payload}
    )

def access_secret(secret_id):
    """Acceder secreto"""
    
    client = secretmanager.SecretManagerServiceClient()
    
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    
    return response.payload.data.decode('UTF-8')
```

### 16.2 Configuración de IAM

```bash
# Principio de mínimo privilegio
gcloud projects add-iam-policy-binding pinad-production \
  --member="serviceAccount:pinad-functions@pinad-production.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker" \
  --condition="title=Cloud Functions Invoker,expression=resource.type == 'cloudfunctions.googleapis.com' && resource.name.startsWith('projects/pinad-production/locations/us-central1/functions/')"
```

### 16.3 Configuración de VPC Service Controls

```bash
# Crear perimeter de servicio
gcloud access-context-manager perimeters create \
  --title="PINAD Perimeter" \
  --resources=projects/pinad-production \
  --restricted-services=cloudfunctions.googleapis.com,run.googleapis.com,sqladmin.googleapis.com
```

---

## CONCLUSIÓN

Esta guía proporciona una implementación técnica completa del sistema (π)NAD, desde la configuración inicial de Google Cloud hasta el despliegue en producción. Sigue esta guía paso a paso para implementar el sistema de manera segura y escalable.

Para soporte técnico adicional, contacta a: tech-support@pinad.com
