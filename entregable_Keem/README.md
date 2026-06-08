# Entregable Keem - Sistema de Escaneo Contable Multi-tenant

## Fecha
Junio 7, 2026

## Descripción General
Este entregable contiene el diseño completo de un sistema de escaneo contable en línea con arquitectura multi-tenant, motor de OCR con IA, dashboard inteligente para clientes, y visión futura de agentes de IA independientes.

---

## Contenido del Entregable

### 1. ANÁLISIS_ESTADO_ACTUAL.md
Análisis comparativo entre el estado actual del sistema contable y la visión requerida.

**Puntos clave:**
- Estamos **60% alejados** de completar el punto 2 (aplicación web de escaneo)
- Estamos **100% alejados** del punto 3 (agentes de IA independientes)
- Tenemos el motor OCR implementado pero falta la configuración web
- Falta el multi-tenancy y el dashboard para clientes

### 2. ARQUITECTURA_WEB.md
Diseño completo de la arquitectura para la aplicación web de escaneo en línea.

**Componentes:**
- Frontend: Flutter Web con escaneo de cámara web
- Backend: Cloud Functions (Node.js/TypeScript)
- Base de datos: Firestore (NoSQL) + Cloud SQL (PostgreSQL)
- Motor OCR: Document AI + Vertex AI
- Hosting: Firebase Hosting

**Características:**
- Escaneo desde navegador
- Procesamiento automático con OCR
- Dashboard inteligente para clientes
- Sistema de retención y recuperación de datos

**Tiempo estimado:** 6-10 semanas

### 3. CONFIGURACION_BASE_DATOS.md
Configuración detallada de Firestore y Cloud SQL para Google Cloud.

**Firestore (NoSQL):**
- Colecciones: tenants, users, documents, document_history, notifications
- Reglas de seguridad multi-tenant
- Índices compuestos para consultas eficientes

**Cloud SQL (PostgreSQL):**
- Tablas: tenants, users, clients, accounts, transactions, journal_entries, journal_entry_lines, audit_log, quotas
- Triggers para actualizar timestamps
- Funciones para verificar balance de asientos
- Backup automático y manual

**Seguridad:**
- Secret Manager para credenciales
- IAM para permisos
- Monitoreo con Cloud Monitoring

### 4. MOTOR_OCR_CLOUD_FUNCTIONS.md
Implementación del motor de escaneo con OCR en Cloud Functions.

**Tecnologías:**
- Google Document AI para OCR básico
- Vertex AI para extracción inteligente de datos
- Cloud Functions para backend serverless
- Cloud Storage para almacenamiento de documentos

**Funciones implementadas:**
- `uploadDocument`: Subir documento a Cloud Storage
- `processDocument`: Procesar documento con OCR (trigger)
- `getDocuments`: Obtener documentos del cliente
- `getDashboardData`: Obtener datos del dashboard

**Servicios:**
- DocumentService: Gestión de documentos
- OCRService: Procesamiento OCR
- ExtractionService: Extracción de datos
- DatabaseService: Persistencia en base de datos

### 5. DASHBOARD_INTELIGENTE_CLIENTES.md
Desarrollo del dashboard inteligente para clientes en Flutter Web.

**Componentes del dashboard:**
- Sidebar de navegación
- Header con perfil y notificaciones
- Tarjetas de resumen (métricas)
- Gráfico de procesamiento (PieChart)
- Lista de documentos recientes
- Tabla de transacciones extraídas
- Panel de alertas

**Características inteligentes:**
- Predicciones de gastos
- Detección de anomalías
- Visualización en tiempo real
- Exportación de datos

**Identidad visual:**
- Colores de PINAD (dorado, marrón, naranja)
- Tipografía LEAGUE GOTHIC y POPPINS LIGHT
- Diseño responsivo

### 6. SISTEMA_MULTI_TENANCY.md
Implementación del sistema multi-tenancy para vender a otros contadores.

**Roles y permisos:**
- Super Admin (PINAD): Gestión global de tenants
- Tenant Admin (Contador): Gestión de su tenant y clientes
- Client (Cliente del contador): Escaneo y visualización
- Viewer (Solo lectura): Solo visualización
- Support (Soporte técnico): Acceso limitado para soporte

**Características:**
- Aislamiento completo de datos por tenant
- Panel de control para contadores
- Gestión de clientes
- Planes: Basic, Pro, Enterprise
- Facturación integrada con Stripe
- Monitoreo de cuotas con alertas

**Panel de control del Tenant Admin:**
- Estadísticas de uso (usuarios, documentos, almacenamiento)
- Lista de clientes
- Opción de actualización de plan
- Configuración del tenant

**Panel de control del Super Admin:**
- Gestión de tenants
- Monitoreo de ingresos
- Creación de nuevos tenants
- Soporte técnico

### 7. ARQUITECTURA_AGENTES_IA.md
Diseño de la arquitectura de agentes de IA independientes (visión futura).

**Principios de diseño:**
- Independencia de agentes (microservicios)
- Modularidad (responsabilidad única)
- Consistencia eventual (event-driven)
- Resiliencia (retry, backoff, dead letter queues)

**Agentes implementados:**
- **Agente OCR**: Procesar documentos con Document AI
- **Agente Extracción**: Extraer datos con Vertex AI
- **Agente Validación**: Validar datos con reglas
- **Agente Clasificación**: Clasificar transacciones
- **Agente Contabilidad**: Crear asientos contables
- **Agente Reportes**: Generar reportes
- **Agente Anomalías**: Detectar anomalías
- **Agente Predicción**: Predecir gastos e ingresos
- **Agente Notificación**: Enviar alertas

**Orquestador de agentes:**
- Coordinar ejecución de agentes
- Manejar dependencias entre agentes
- Gestionar estado de procesos
- Recuperación de errores

**Manejo de conflictos:**
- Sistema de versionamiento de eventos
- Sistema de compensación (SAGA pattern)
- Estrategias de resolución: last-write-wins, merge, manual

**Despliegue:**
- Kubernetes para escalabilidad
- Pub/Sub para comunicación entre agentes
- Monitoreo con Cloud Monitoring

---

## Arquitectura General del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cliente (Navegador)                          │
│  Flutter Web App - Escaneo + Dashboard                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Firebase Hosting                                         │  │
│  │  Hosting de aplicación web Flutter                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud Functions (Backend)                               │  │
│  │  - uploadDocument, processDocument                       │  │
│  │  - getDashboardData, getDocuments                        │  │
│  │  - createTenant, updateTenant, deleteTenant              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud Pub/Sub (Event Bus)                               │  │
│  │  - document.uploaded, document.processed                │  │
│  │  - transaction.created, transaction.updated              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document AI + Vertex AI (Motor OCR)                      │  │
│  │  - Procesamiento OCR                                     │  │
│  │  - Extracción inteligente de datos                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Firestore (NoSQL)                                       │  │
│  │  - Documentos, usuarios, tenants, notificaciones       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud SQL (PostgreSQL)                                  │  │
│  │  - Transacciones, asientos, clientes, cuentas            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud Storage                                            │  │
│  │  - Almacenamiento de documentos                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Visión Futura: Agentes de IA Independientes

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orquestador de Agentes                        │
│  - Coordinar ejecución de agentes                              │
│  - Manejar dependencias entre agentes                          │
│  - Gestionar estado de procesos                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Pub/Sub
                              │
        ┌─────────────┬─────────────┬─────────────┬─────────────┐
        │             │             │             │             │
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Agente OCR    │ │ Agente       │ │ Agente       │ │ Agente       │
│               │ │ Extracción    │ │ Validación   │ │ Contabilidad │
│ - Procesar    │ │ - Extraer     │ │ - Validar    │ │ - Crear      │
│   documentos  │ │   datos       │ │   datos      │ │   asientos   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┴─────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Agente       │ │ Agente       │ │ Agente       │
│ Anomalías     │ │ Predicción    │ │ Notificación │
│ - Detectar    │ │ - Predecir    │ │ - Enviar     │
│   anomalías   │ │   gastos      │ │   alertas    │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## Planes de Implementación

### Plan Básico
- **Usuarios:** 5
- **Documentos:** 1,000
- **Almacenamiento:** 10 GB
- **Precio:** $49/mes

### Plan Profesional
- **Usuarios:** 25
- **Documentos:** 10,000
- **Almacenamiento:** 100 GB
- **Precio:** $99/mes

### Plan Empresarial
- **Usuarios:** 100
- **Documentos:** 100,000
- **Almacenamiento:** 1 TB
- **Precio:** $299/mes

---

## Tecnologías Utilizadas

### Frontend
- **Flutter Web**: Framework para aplicación web
- **Flutter Bloc**: State management
- **Google Fonts**: LEAGUE GOTHIC y POPPINS LIGHT
- **FL Chart**: Gráficos para dashboard

### Backend
- **Cloud Functions**: Backend serverless (Node.js/TypeScript)
- **Document AI**: Procesamiento OCR
- **Vertex AI**: Extracción inteligente de datos
- **Pub/Sub**: Bus de mensajes para agentes

### Base de Datos
- **Firestore**: NoSQL para documentos y metadatos
- **Cloud SQL**: PostgreSQL para datos estructurados
- **Cloud Storage**: Almacenamiento de archivos

### Infraestructura
- **Firebase Hosting**: Hosting de aplicación web
- **Kubernetes**: Orquestación de agentes (visión futura)
- **Cloud Monitoring**: Monitoreo y alertas
- **Secret Manager**: Gestión de secretos

### Pagos
- **Stripe**: Facturación y pagos

---

## Estimación de Tiempos

### Fase 1: Configuración Base (1-2 semanas)
- Configurar Flutter Web
- Configurar Firebase Hosting
- Configurar Cloud Storage
- Configurar Firestore
- Configurar Cloud SQL

### Fase 2: Backend (2-3 semanas)
- Implementar Cloud Functions
- Integrar Document AI
- Integrar Vertex AI
- Implementar multi-tenancy
- Implementar sistema de roles

### Fase 3: Frontend (2-3 semanas)
- Implementar escaneo con cámara web
- Implementar dashboard para clientes
- Implementar autenticación multi-tenant
- Implementar visualización de documentos
- Implementar exportación de datos

### Fase 4: Testing y Despliegue (1-2 semanas)
- Testing unitario
- Testing de integración
- Testing E2E
- Despliegue en Google Cloud
- Configurar monitoreo y alertas

**Total: 6-10 semanas** para completar la aplicación web de escaneo en línea con dashboard inteligente y multi-tenancy.

---

## Próximos Pasos

### Inmediatos (Punto 2)
1. Configurar proyecto en Google Cloud
2. Configurar Flutter Web
3. Implementar Cloud Functions
4. Desarrollar dashboard para clientes
5. Implementar multi-tenancy
6. Desplegar en producción

### Futuros (Punto 3)
1. Diseñar arquitectura de agentes
2. Implementar orquestador de agentes
3. Desarrollar agentes independientes
4. Implementar sistema de eventos
5. Implementar manejo de conflictos
6. Desplegar en Kubernetes

---

## Conclusión

Este entregable proporciona una visión completa del sistema de escaneo contable multi-tenant, desde el análisis del estado actual hasta la arquitectura de agentes de IA independientes. El sistema está diseñado para ser escalable, modular, y resiliente, con la capacidad de vender la plataforma a otros contadores como un servicio SaaS.

La prioridad inmediata es completar el punto 2 (aplicación web de escaneo en línea), mientras que el punto 3 (agentes de IA independientes) es una visión futura que permitirá cambios en el registro de ventas sin conflictos en el sistema.
