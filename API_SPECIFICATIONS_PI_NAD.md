# ESPECIFICACIONES DE API - Sistema (π)NAD

## ÍNDICE

1. [Visión General de la API](#1-visión-general-de-la-api)
2. [Autenticación y Autorización](#2-autenticación-y-autorización)
3. [Endpoints de Clientes](#3-endpoints-de-clientes)
4. [Endpoints de Documentos](#4-endpoints-de-documentos)
5. [Endpoints de Transacciones](#5-endpoints-de-transacciones)
6. [Endpoints de Validación](#6-endpoints-de-validación)
7. [Endpoints de Dashboard](#7-endpoints-de-dashboard)
8. [Webhooks](#8-webhooks)
9. [Códigos de Error](#9-códigos-de-error)
10. [Ejemplos de Uso](#10-ejemplos-de-uso)

---

## 1. VISIÓN GENERAL DE LA API

### 1.1 Información Base

**URL Base:** `https://api.pinad.com/v1`

**Versión:** v1.0.0

**Formato de Datos:** JSON

**Codificación:** UTF-8

**Rate Limiting:**
- Plan Básico: 100 requests/hora
- Plan Profesional: 1,000 requests/hora
- Plan Enterprise: 10,000 requests/hora

### 1.2 Headers Requeridos

```
Content-Type: application/json
Authorization: Bearer {access_token}
X-API-Key: {api_key}
X-Client-ID: {client_id}
```

### 1.3 Respuestas Estándar

**Éxito:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operación exitosa",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descripción del error",
    "details": { ... }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 2. AUTENTICACIÓN Y AUTORIZACIÓN

### 2.1 OAuth 2.0 - Obtener Access Token

**Endpoint:** `POST /auth/oauth/token`

**Request Body:**
```json
{
  "grant_type": "authorization_code",
  "code": "authorization_code_from_google",
  "redirect_uri": "https://app.pinad.com/callback",
  "client_id": "client_id",
  "client_secret": "client_secret"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "ya29.a0AfH6SMB...",
    "refresh_token": "1//0g...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "read write"
  }
}
```

### 2.2 Refresh Token

**Endpoint:** `POST /auth/oauth/refresh`

**Request Body:**
```json
{
  "grant_type": "refresh_token",
  "refresh_token": "refresh_token"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token",
    "refresh_token": "new_refresh_token",
    "expires_in": 3600
  }
}
```

### 2.3 Verificar Token

**Endpoint:** `GET /auth/verify`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user_id": "user_id",
    "email": "user@gmail.com",
    "role": "client",
    "expires_at": "2024-01-01T13:00:00Z"
  }
}
```

---

## 3. ENDPOINTS DE CLIENTES

### 3.1 Registrar Cliente

**Endpoint:** `POST /clients`

**Request Body:**
```json
{
  "rif": "J-12345678-9",
  "name": "Empresa ABC C.A.",
  "email": "contacto@empresaabc.com",
  "phone": "+58-414-123-4567",
  "sector": "comercio",
  "plan": "profesional",
  "address": {
    "street": "Av. Principal",
    "city": "Caracas",
    "state": "Distrito Capital",
    "zip": "1010"
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "client_id": "client_uuid",
    "rif": "J-12345678-9",
    "name": "Empresa ABC C.A.",
    "status": "active",
    "created_at": "2024-01-01T12:00:00Z",
    "google_drive_folder_id": "folder_id"
  }
}
```

### 3.2 Obtener Información de Cliente

**Endpoint:** `GET /clients/{client_id}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "client_id": "client_uuid",
    "rif": "J-12345678-9",
    "name": "Empresa ABC C.A.",
    "email": "contacto@empresaabc.com",
    "phone": "+58-414-123-4567",
    "sector": "comercio",
    "plan": "profesional",
    "status": "active",
    "subscription": {
      "plan": "profesional",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "transaction_limit": 500,
      "users_limit": 3
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 3.3 Actualizar Cliente

**Endpoint:** `PUT /clients/{client_id}`

**Request Body:**
```json
{
  "name": "Empresa ABC C.A. (Actualizado)",
  "phone": "+58-414-999-9999",
  "address": {
    "street": "Av. Nueva",
    "city": "Caracas",
    "state": "Distrito Capital",
    "zip": "1010"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "client_id": "client_uuid",
    "name": "Empresa ABC C.A. (Actualizado)",
    "updated_at": "2024-01-20T15:00:00Z"
  }
}
```

### 3.4 Listar Clientes (Solo Asesores/Admin)

**Endpoint:** `GET /clients`

**Query Parameters:**
- `page`: Número de página (default: 1)
- `limit`: Resultados por página (default: 20)
- `status`: Filtrar por estado (active, inactive, pending)
- `sector`: Filtrar por sector
- `search`: Búsqueda por nombre o RIF

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "clients": [
      {
        "client_id": "client_uuid_1",
        "rif": "J-12345678-9",
        "name": "Empresa ABC C.A.",
        "status": "active",
        "sector": "comercio"
      },
      {
        "client_id": "client_uuid_2",
        "rif": "V-98765432-1",
        "name": "Dr. Juan Pérez",
        "status": "active",
        "sector": "servicios"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "total_pages": 8
    }
  }
}
```

---

## 4. ENDPOINTS DE DOCUMENTOS

### 4.1 Subir Documento

**Endpoint:** `POST /documents`

**Request Body (multipart/form-data):**
```
file: [archivo]
client_id: client_uuid
document_type: report_z | invoice_sale | invoice_purchase | database
period: 2024-01
notes: (opcional)
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "document_id": "document_uuid",
    "client_id": "client_uuid",
    "file_name": "reporte_z_enero.pdf",
    "file_type": "pdf",
    "document_type": "report_z",
    "file_size": 1048576,
    "upload_date": "2024-01-15T10:00:00Z",
    "processing_status": "pending",
    "google_drive_file_id": "drive_file_id"
  }
}
```

### 4.2 Subir Múltiples Documentos

**Endpoint:** `POST /documents/batch`

**Request Body (multipart/form-data):**
```
files: [archivo1, archivo2, archivo3]
client_id: client_uuid
document_type: invoice_sale
period: 2024-01
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "uploaded": 3,
    "documents": [
      {
        "document_id": "doc_uuid_1",
        "file_name": "factura_001.pdf",
        "status": "pending"
      },
      {
        "document_id": "doc_uuid_2",
        "file_name": "factura_002.pdf",
        "status": "pending"
      },
      {
        "document_id": "doc_uuid_3",
        "file_name": "factura_003.pdf",
        "status": "pending"
      }
    ]
  }
}
```

### 4.3 Obtener Estado de Documento

**Endpoint:** `GET /documents/{document_id}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "document_id": "document_uuid",
    "client_id": "client_uuid",
    "file_name": "reporte_z_enero.pdf",
    "document_type": "report_z",
    "upload_date": "2024-01-15T10:00:00Z",
    "processing_status": "completed",
    "ocr_confidence": 0.95,
    "extraction_date": "2024-01-15T10:30:00Z",
    "extracted_data": {
      "report_date": "2024-01-31",
      "report_number": "Z-001",
      "total_sales": 25000.00,
      "total_tax": 4000.00,
      "cash_sales": 15000.00,
      "credit_sales": 10000.00,
      "returns": 500.00
    }
  }
}
```

### 4.4 Listar Documentos de Cliente

**Endpoint:** `GET /clients/{client_id}/documents`

**Query Parameters:**
- `document_type`: Filtrar por tipo
- `status`: Filtrar por estado (pending, processing, completed, error)
- `period`: Filtrar por período (YYYY-MM)
- `page`: Número de página
- `limit`: Resultados por página

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "document_id": "doc_uuid_1",
        "file_name": "reporte_z_enero.pdf",
        "document_type": "report_z",
        "upload_date": "2024-01-15T10:00:00Z",
        "processing_status": "completed",
        "ocr_confidence": 0.95
      },
      {
        "document_id": "doc_uuid_2",
        "file_name": "factura_001.pdf",
        "document_type": "invoice_sale",
        "upload_date": "2024-01-16T11:00:00Z",
        "processing_status": "pending"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

### 4.5 Eliminar Documento

**Endpoint:** `DELETE /documents/{document_id}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Documento eliminado exitosamente"
}
```

---

## 5. ENDPOINTS DE TRANSACCIONES

### 5.1 Obtener Transacción

**Endpoint:** `GET /transactions/{transaction_id}`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transaction_id": "transaction_uuid",
    "client_id": "client_uuid",
    "document_id": "document_uuid",
    "transaction_date": "2024-01-15",
    "type": "sale",
    "amount": 1500.00,
    "tax_amount": 240.00,
    "tax_rate": 16.00,
    "description": "Venta de productos",
    "category": "Ventas de Productos",
    "status": "validated",
    "extracted_data": {
      "invoice_number": "F001-0001234",
      "customer_rif": "V-11111111-1",
      "customer_name": "Cliente XYZ"
    },
    "validation_notes": "Datos correctos",
    "validated_by": "advisor_uuid",
    "validation_date": "2024-01-16T09:00:00Z",
    "created_at": "2024-01-15T12:00:00Z"
  }
}
```

### 5.2 Listar Transacciones

**Endpoint:** `GET /clients/{client_id}/transactions`

**Query Parameters:**
- `type`: Filtrar por tipo (sale, purchase, expense)
- `status`: Filtrar por estado (pending, validated, rejected)
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)
- `category`: Filtrar por categoría
- `page`: Número de página
- `limit`: Resultados por página

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "transaction_id": "txn_uuid_1",
        "transaction_date": "2024-01-15",
        "type": "sale",
        "amount": 1500.00,
        "tax_amount": 240.00,
        "category": "Ventas de Productos",
        "status": "validated"
      },
      {
        "transaction_id": "txn_uuid_2",
        "transaction_date": "2024-01-16",
        "type": "purchase",
        "amount": 800.00,
        "tax_amount": 128.00,
        "category": "Compras de Inventario",
        "status": "validated"
      }
    ],
    "summary": {
      "total_revenue": 25000.00,
      "total_expenses": 18000.00,
      "net_income": 7000.00,
      "transaction_count": 45
    },
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

### 5.3 Crear Transacción Manual

**Endpoint:** `POST /transactions`

**Request Body:**
```json
{
  "client_id": "client_uuid",
  "transaction_date": "2024-01-15",
  "type": "sale",
  "amount": 1500.00,
  "tax_amount": 240.00,
  "tax_rate": 16.00,
  "description": "Venta manual",
  "category": "Ventas de Productos"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "transaction_id": "transaction_uuid",
    "status": "pending",
    "created_at": "2024-01-15T12:00:00Z"
  }
}
```

### 5.4 Actualizar Transacción

**Endpoint:** `PUT /transactions/{transaction_id}`

**Request Body:**
```json
{
  "amount": 1600.00,
  "tax_amount": 256.00,
  "description": "Venta actualizada",
  "category": "Ventas de Servicios"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transaction_id": "transaction_uuid",
    "amount": 1600.00,
    "tax_amount": 256.00,
    "updated_at": "2024-01-16T10:00:00Z"
  }
}
```

### 5.5 Eliminar Transacción

**Endpoint:** `DELETE /transactions/{transaction_id}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Transacción eliminada exitosamente"
}
```

---

## 6. ENDPOINTS DE VALIDACIÓN

### 6.1 Validar Transacción (Solo Asesores)

**Endpoint:** `POST /transactions/{transaction_id}/validate`

**Request Body:**
```json
{
  "action": "approve",
  "notes": "Datos correctos, conciliación verificada"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transaction_id": "transaction_uuid",
    "status": "validated",
    "validated_by": "advisor_uuid",
    "validation_date": "2024-01-16T09:00:00Z",
    "validation_notes": "Datos correctos, conciliación verificada"
  }
}
```

### 6.2 Rechazar Transacción (Solo Asesores)

**Endpoint:** `POST /transactions/{transaction_id}/reject`

**Request Body:**
```json
{
  "action": "reject",
  "notes": "Monto incorrecto, verificar factura original"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transaction_id": "transaction_uuid",
    "status": "rejected",
    "validated_by": "advisor_uuid",
    "validation_date": "2024-01-16T09:00:00Z",
    "validation_notes": "Monto incorrecto, verificar factura original"
  }
}
```

### 6.3 Agregar Observación (Solo Asesores)

**Endpoint:** `POST /transactions/{transaction_id}/observe`

**Request Body:**
```json
{
  "action": "observe",
  "notes": "Monto correcto pero categoría debe ser revisada"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transaction_id": "transaction_uuid",
    "status": "validated",
    "validated_by": "advisor_uuid",
    "validation_date": "2024-01-16T09:00:00Z",
    "validation_notes": "Monto correcto pero categoría debe ser revisada"
  }
}
```

### 6.4 Obtener Historial de Validación

**Endpoint:** `GET /transactions/{transaction_id}/validation-history`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "log_id": "log_uuid_1",
        "validator_id": "advisor_uuid",
        "validator_name": "Asesor Contable",
        "action": "approved",
        "notes": "Datos correctos",
        "previous_status": "pending",
        "new_status": "validated",
        "timestamp": "2024-01-16T09:00:00Z"
      }
    ]
  }
}
```

### 6.5 Listar Transacciones Pendientes de Validación (Solo Asesores)

**Endpoint:** `GET /advisors/{advisor_id}/pending-validations`

**Query Parameters:**
- `client_id`: Filtrar por cliente (opcional)
- `priority`: Filtrar por prioridad (high, medium, low)
- `page`: Número de página
- `limit`: Resultados por página

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "transaction_id": "txn_uuid_1",
        "client_id": "client_uuid",
        "client_name": "Empresa ABC",
        "transaction_date": "2024-01-15",
        "type": "sale",
        "amount": 1500.00,
        "priority": "high",
        "pending_since": "2024-01-15T12:00:00Z"
      }
    ],
    "summary": {
      "total_pending": 15,
      "high_priority": 5,
      "medium_priority": 8,
      "low_priority": 2
    },
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 15,
      "total_pages": 1
    }
  }
}
```

---

## 7. ENDPOINTS DE DASHBOARD

### 7.1 Obtener Resumen Ejecutivo

**Endpoint:** `GET /clients/{client_id}/dashboard/summary`

**Query Parameters:**
- `period`: Período (YYYY-MM, YYYY, all)
- `compare_with`: Período a comparar (YYYY-MM)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "period": "2024-01",
    "revenue": {
      "total": 25000.00,
      "previous_period": 22000.00,
      "variation": 13.64,
      "variation_type": "positive"
    },
    "expenses": {
      "total": 18000.00,
      "previous_period": 19500.00,
      "variation": -7.69,
      "variation_type": "positive"
    },
    "net_income": {
      "total": 7000.00,
      "previous_period": 2500.00,
      "variation": 180.00,
      "variation_type": "positive"
    },
    "margin": {
      "percentage": 28.00,
      "previous_period": 11.36,
      "variation": 16.64,
      "variation_type": "positive"
    },
    "transactions": {
      "total": 45,
      "sales": 30,
      "purchases": 15,
      "average_transaction": 555.56
    }
  }
}
```

### 7.2 Obtener Datos de Gráficos

**Endpoint:** `GET /clients/{client_id}/dashboard/charts`

**Query Parameters:**
- `chart_type`: Tipo de gráfico (revenue_trend, expense_distribution, comparison)
- `period`: Período (YYYY-MM, YYYY, all)
- `granularity`: Granularidad (daily, weekly, monthly)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "chart_type": "revenue_trend",
    "period": "2024-01",
    "granularity": "daily",
    "data": [
      {
        "date": "2024-01-01",
        "revenue": 800.00,
        "expenses": 500.00,
        "net_income": 300.00
      },
      {
        "date": "2024-01-02",
        "revenue": 1200.00,
        "expenses": 600.00,
        "net_income": 600.00
      }
    ]
  }
}
```

### 7.3 Obtener Distribución por Categoría

**Endpoint:** `GET /clients/{client_id}/dashboard/categories`

**Query Parameters:**
- `type`: Tipo (revenue, expenses)
- `period`: Período (YYYY-MM, YYYY, all)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "type": "expenses",
    "period": "2024-01",
    "categories": [
      {
        "category": "Compras de Inventario",
        "amount": 8000.00,
        "percentage": 44.44,
        "transaction_count": 10
      },
      {
        "category": "Servicios Básicos",
        "amount": 4000.00,
        "percentage": 22.22,
        "transaction_count": 5
      },
      {
        "category": "Nómina",
        "amount": 6000.00,
        "percentage": 33.33,
        "transaction_count": 1
      }
    ]
  }
}
```

### 7.4 Exportar Datos

**Endpoint:** `GET /clients/{client_id}/dashboard/export`

**Query Parameters:**
- `format`: Formato (csv, xlsx, pdf)
- `period`: Período (YYYY-MM, YYYY, all)
- `include_charts`: Incluir gráficos (true, false)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "export_id": "export_uuid",
    "format": "xlsx",
    "status": "processing",
    "download_url": null,
    "expires_at": "2024-01-17T12:00:00Z"
  }
}
```

**Response (200 OK) - Cuando está listo:**
```json
{
  "success": true,
  "data": {
    "export_id": "export_uuid",
    "format": "xlsx",
    "status": "completed",
    "download_url": "https://api.pinad.com/exports/export_uuid.xlsx",
    "file_size": 1048576,
    "expires_at": "2024-01-17T12:00:00Z"
  }
}
```

---

## 8. WEBHOOKS

### 8.1 Configurar Webhook

**Endpoint:** `POST /webhooks`

**Request Body:**
```json
{
  "client_id": "client_uuid",
  "url": "https://your-domain.com/webhook",
  "events": [
    "document.uploaded",
    "document.processed",
    "transaction.validated",
    "transaction.rejected"
  ],
  "secret": "your_webhook_secret"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "webhook_id": "webhook_uuid",
    "url": "https://your-domain.com/webhook",
    "events": [
      "document.uploaded",
      "document.processed",
      "transaction.validated",
      "transaction.rejected"
    ],
    "status": "active",
    "created_at": "2024-01-15T12:00:00Z"
  }
}
```

### 8.2 Listar Webhooks

**Endpoint:** `GET /clients/{client_id}/webhooks`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "webhook_id": "webhook_uuid",
        "url": "https://your-domain.com/webhook",
        "events": ["document.processed"],
        "status": "active",
        "created_at": "2024-01-15T12:00:00Z"
      }
    ]
  }
}
```

### 8.3 Eliminar Webhook

**Endpoint:** `DELETE /webhooks/{webhook_id}`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Webhook eliminado exitosamente"
}
```

### 8.4 Eventos de Webhook

**Evento: document.uploaded**
```json
{
  "event": "document.uploaded",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "document_id": "document_uuid",
    "client_id": "client_uuid",
    "file_name": "factura.pdf",
    "document_type": "invoice_sale",
    "upload_date": "2024-01-15T12:00:00Z"
  }
}
```

**Evento: document.processed**
```json
{
  "event": "document.processed",
  "timestamp": "2024-01-15T12:30:00Z",
  "data": {
    "document_id": "document_uuid",
    "client_id": "client_uuid",
    "processing_status": "completed",
    "ocr_confidence": 0.95,
    "extracted_data": { ... }
  }
}
```

**Evento: transaction.validated**
```json
{
  "event": "transaction.validated",
  "timestamp": "2024-01-16T09:00:00Z",
  "data": {
    "transaction_id": "transaction_uuid",
    "client_id": "client_uuid",
    "status": "validated",
    "validated_by": "advisor_uuid",
    "validation_notes": "Datos correctos"
  }
}
```

---

## 9. CÓDIGOS DE ERROR

### 9.1 Códigos Generales

| Código | Descripción | HTTP Status |
|--------|-------------|-------------|
| AUTH_001 | Token inválido o expirado | 401 |
| AUTH_002 | Permisos insuficientes | 403 |
| AUTH_003 | Usuario no encontrado | 404 |
| REQ_001 | Parámetros inválidos | 400 |
| REQ_002 | Formato de archivo no soportado | 400 |
| REQ_003 | Tamaño de archivo excedido | 400 |
| SRV_001 | Error interno del servidor | 500 |
| SRV_002 | Servicio no disponible | 503 |
| RATE_001 | Límite de rate excedido | 429 |

### 9.2 Códigos de Clientes

| Código | Descripción | HTTP Status |
|--------|-------------|-------------|
| CLI_001 | Cliente no encontrado | 404 |
| CLI_002 | RIF ya registrado | 409 |
| CLI_003 | Email ya registrado | 409 |
| CLI_004 | Cliente inactivo | 403 |
| CLI_005 | Límite de transacciones excedido | 403 |

### 9.3 Códigos de Documentos

| Código | Descripción | HTTP Status |
|--------|-------------|-------------|
| DOC_001 | Documento no encontrado | 404 |
| DOC_002 | Error en procesamiento OCR | 500 |
| DOC_003 | Archivo corrupto | 400 |
| DOC_004 | Documento ya procesado | 409 |
| DOC_005 | Tipo de documento inválido | 400 |

### 9.4 Códigos de Transacciones

| Código | Descripción | HTTP Status |
|--------|-------------|-------------|
| TXN_001 | Transacción no encontrada | 404 |
| TXN_002 | Transacción ya validada | 409 |
| TXN_003 | Monto inválido | 400 |
| TXN_004 | Fecha inválida | 400 |
| TXN_005 | Categoría inválida | 400 |

### 9.5 Códigos de Validación

| Código | Descripción | HTTP Status |
|--------|-------------|-------------|
| VAL_001 | Solo asesores pueden validar | 403 |
| VAL_002 | Transacción no pendiente | 409 |
| VAL_003 | Asesor no asignado al cliente | 403 |

---

## 10. EJEMPLOS DE USO

### 10.1 Ejemplo 1: Flujo Completo de Carga

```python
import requests

# Configuración
BASE_URL = "https://api.pinad.com/v1"
ACCESS_TOKEN = "your_access_token"
API_KEY = "your_api_key"
CLIENT_ID = "client_uuid"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-API-Key": API_KEY,
    "X-Client-ID": CLIENT_ID,
    "Content-Type": "application/json"
}

# Paso 1: Subir documento
with open("factura.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "client_id": CLIENT_ID,
        "document_type": "invoice_sale",
        "period": "2024-01"
    }
    response = requests.post(
        f"{BASE_URL}/documents",
        headers=headers,
        files=files,
        data=data
    )
    document = response.json()["data"]
    print(f"Documento subido: {document['document_id']}")

# Paso 2: Verificar estado
document_id = document["document_id"]
response = requests.get(
    f"{BASE_URL}/documents/{document_id}",
    headers=headers
)
status = response.json()["data"]
print(f"Estado: {status['processing_status']}")

# Paso 3: Esperar procesamiento
import time
time.sleep(60)  # Esperar 1 minuto

# Paso 4: Verificar resultado
response = requests.get(
    f"{BASE_URL}/documents/{document_id}",
    headers=headers
)
result = response.json()["data"]
print(f"Confianza OCR: {result['ocr_confidence']}")
print(f"Datos extraídos: {result['extracted_data']}")
```

### 10.2 Ejemplo 2: Validación por Asesor

```python
import requests

# Configuración
BASE_URL = "https://api.pinad.com/v1"
ACCESS_TOKEN = "advisor_access_token"
API_KEY = "advisor_api_key"
TRANSACTION_ID = "transaction_uuid"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Paso 1: Obtener transacción pendiente
response = requests.get(
    f"{BASE_URL}/transactions/{TRANSACTION_ID}",
    headers=headers
)
transaction = response.json()["data"]
print(f"Transacción: {transaction['amount']}")

# Paso 2: Validar transacción
validation_data = {
    "action": "approve",
    "notes": "Datos correctos, conciliación verificada"
}
response = requests.post(
    f"{BASE_URL}/transactions/{TRANSACTION_ID}/validate",
    headers=headers,
    json=validation_data
)
result = response.json()["data"]
print(f"Estado: {result['status']}")
```

### 10.3 Ejemplo 3: Obtener Dashboard

```python
import requests

# Configuración
BASE_URL = "https://api.pinad.com/v1"
ACCESS_TOKEN = "client_access_token"
API_KEY = "client_api_key"
CLIENT_ID = "client_uuid"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-API-Key": API_KEY,
    "X-Client-ID": CLIENT_ID
}

# Paso 1: Obtener resumen ejecutivo
params = {"period": "2024-01"}
response = requests.get(
    f"{BASE_URL}/clients/{CLIENT_ID}/dashboard/summary",
    headers=headers,
    params=params
)
summary = response.json()["data"]
print(f"Ingresos: ${summary['revenue']['total']}")
print(f"Egresos: ${summary['expenses']['total']}")
print(f"Ingreso Neto: ${summary['net_income']['total']}")

# Paso 2: Obtener datos de gráficos
params = {
    "chart_type": "revenue_trend",
    "period": "2024-01",
    "granularity": "daily"
}
response = requests.get(
    f"{BASE_URL}/clients/{CLIENT_ID}/dashboard/charts",
    headers=headers,
    params=params
}
chart_data = response.json()["data"]
print(f"Datos de gráfico: {len(chart_data['data'])} puntos")
```

### 10.4 Ejemplo 4: Webhook

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verificar firma (opcional)
    signature = request.headers.get('X-Webhook-Signature')
    # Implementar verificación de firma
    
    # Procesar evento
    payload = request.json
    event = payload.get('event')
    data = payload.get('data')
    
    if event == 'document.processed':
        document_id = data.get('document_id')
        print(f"Documento procesado: {document_id}")
        # Realizar acción personalizada
    
    elif event == 'transaction.validated':
        transaction_id = data.get('transaction_id')
        print(f"Transacción validada: {transaction_id}")
        # Realizar acción personalizada
    
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=5000)
```

---

## CONCLUSIÓN

Esta especificación de API proporciona una base completa para la integración con el sistema (π)NAD. Los endpoints están diseñados para ser RESTful, consistentes y fáciles de usar, con documentación clara de parámetros, respuestas y códigos de error.

La API soporta todas las funcionalidades principales del sistema:
- Gestión de clientes
- Carga y procesamiento de documentos
- Gestión de transacciones
- Validación profesional
- Dashboards y reportes
- Webhooks para integraciones

Para más información o soporte, contacte a: api-support@pinad.com
