# Resumen del Proyecto (π)NAD - Sistema de Escaneo Contable

## Fecha
Junio 8, 2026

## Visión General

Sistema de escaneo contable multi-tenancy que permite a contadores procesar documentos, extraer datos de facturas mediante OCR, generar reportes y gestionar clientes de manera automatizada.

## Arquitectura Híbrida

### Firebase (Google Cloud)
- **Hosting**: https://pinad-scanning-system-cbde8.web.app
- **Authentication**: Autenticación de usuarios
- **Analytics**: Análisis de uso
- **Crashlytics**: Reporte de errores
- **Performance**: Monitoreo de rendimiento

### Supabase
- **Database**: PostgreSQL para datos persistentes
- **Storage**: Almacenamiento de documentos
- **Edge Functions**: Funciones serverless para OCR (TypeScript/Deno)

### Google Workspace APIs
- **Gmail API**: Notificaciones por email
- **Drive API**: Backup de datos
- **Sheets API**: Generación de reportes
- **Calendar API**: Recordatorios automáticos

## Componentes del Sistema

### 1. Motor OCR
- **Ubicación**: Supabase Edge Function (`supabase/functions/ocr-process/index.ts`)
- **Tecnología**: TypeScript/Deno con Tesseract.js
- **Funciones**:
  - Extracción de datos de facturas (RIF, número, fecha, montos)
  - Procesamiento asíncrono de documentos
  - Guardado de resultados en Supabase PostgreSQL

### 2. Dashboard de Clientes
- **Ubicación**: `lib/presentation/pages/client/client_dashboard_page.dart`
- **Características**:
  - Métricas en tiempo real (documentos, transacciones, montos)
  - Gráfico de estado de procesamiento
  - Lista de documentos recientes
  - Tabla de transacciones extraídas
  - Panel de alertas

### 3. Sistema Multi-tenancy
- **Ubicación**: `lib/core/services/multi_tenant_service.dart`
- **Roles**:
  - Super Admin: Gestión global del sistema
  - Tenant Admin: Gestión de su tenant y usuarios
  - Client: Escaneo y visualización de documentos
  - Viewer: Solo lectura
  - Support: Soporte técnico
- **Características**:
  - Aislamiento completo de datos por tenant
  - Gestión de usuarios y permisos
  - Métricas de uso por tenant

### 4. Servicios de Google Workspace

#### Gmail Service (`lib/core/services/gmail_service.dart`)
- Notificaciones de documentos procesados
- Notificaciones de nuevos usuarios
- Alertas del sistema
- Reportes generados

#### Drive Service (`lib/core/services/drive_service.dart`)
- Backup automático de datos del tenant
- Subida de documentos a Google Drive
- Gestión de archivos y carpetas
- Compartir archivos con usuarios

#### Sheets Service (`lib/core/services/sheets_service.dart`)
- Generación de reportes de IVA
- Generación de reportes de ISLR
- Reportes de transacciones
- Reportes de documentos

#### Calendar Service (`lib/core/services/calendar_service.dart`)
- Recordatorios de vencimiento de facturas
- Recordatorios de declaraciones de impuestos
- Recordatorios de reportes mensuales
- Recordatorios de reuniones con clientes

## Estructura del Proyecto

```
D:\NAD\pinad_app\
├── lib/
│   ├── core/
│   │   ├── services/
│   │   │   ├── supabase_service.dart
│   │   │   ├── multi_tenant_service.dart
│   │   │   ├── gmail_service.dart
│   │   │   ├── drive_service.dart
│   │   │   ├── sheets_service.dart
│   │   │   └── calendar_service.dart
│   │   └── theme/
│   │       └── app_theme.dart
│   ├── presentation/
│   │   ├── cubit/
│   │   │   ├── dashboard/
│   │   │   │   └── client_dashboard_cubit.dart
│   │   │   └── tenant/
│   │   │       └── tenant_management_cubit.dart
│   │   ├── pages/
│   │   │   ├── client/
│   │   │   │   └── client_dashboard_page.dart
│   │   │   └── admin/
│   │   │       └── tenant_management_page.dart
│   │   └── widgets/
│   │       └── client/
│   │           ├── summary_cards.dart
│   │           ├── processing_chart.dart
│   │           ├── recent_documents.dart
│   │           ├── transactions_table.dart
│   │           └── alerts_panel.dart
│   └── main.dart
├── supabase/
│   └── functions/
│       └── ocr-process/
│           ├── index.ts
│           └── deno.json
├── firebase.json
├── pubspec.yaml
└── INSTRUCCIONES_INSTALACION_FLUTTER.md
```

## Configuración de Credenciales

### Supabase
- **Project URL**: https://rteuftlsbglpgcawsdqz.supabase.co
- **Anon Key**: sb_publishable_eUlKRfeFNvqdURtW_abbIA_N8Qte0l3
- **Service Role Key**: [Configurar en Supabase Dashboard]

### Google Workspace
- **API Key**: AIzaSyAG0gM9rUHowL14Aig5KrMtfdeSxnkYQik
- **Client ID**: 531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com
- **Client Secret**: [Obtener desde Google Cloud Console]

### Firebase
- **Project ID**: pinad-scanning-system
- **Hosting URL**: https://pinad-scanning-system-cbde8.web.app

## Pasos para Desplegar

### 1. Instalar Flutter SDK
Sigue las instrucciones en `INSTRUCCIONES_INSTALACION_FLUTTER.md`

### 2. Actualizar Dependencias
```powershell
cd D:\NAD\pinad_app
flutter pub get
```

### 3. Build de Flutter Web
```powershell
flutter build web
```

### 4. Desplegar en Firebase Hosting
```powershell
firebase deploy
```

### 5. Probar en Producción
Abre: https://pinad-scanning-system-cbde8.web.app

## Base de Datos Supabase

### Tablas
- **tenants**: Información de cada tenant (contador)
- **users**: Usuarios del sistema
- **documents**: Documentos escaneados
- **transactions**: Transacciones extraídas de documentos

### Storage Buckets
- **documents**: Almacenamiento de archivos de documentos

## APIs de Google Workspace

### APIs Habilitadas
- Gmail API
- Google Drive API
- Google Sheets API
- Google Calendar API

### Alcances (Scopes) Requeridos
- Gmail: `https://www.googleapis.com/auth/gmail.send`
- Drive: `https://www.googleapis.com/auth/drive`
- Sheets: `https://www.googleapis.com/auth/spreadsheets`
- Calendar: `https://www.googleapis.com/auth/calendar`

## Características Principales

### Para Contadores (Tenants)
- Gestión de múltiples clientes
- Dashboard de métricas en tiempo real
- Generación automática de reportes
- Backup automático en Google Drive
- Recordatorios automáticos en Google Calendar

### Para Clientes
- Escaneo de documentos
- Visualización de transacciones extraídas
- Descarga de reportes
- Notificaciones por email

### Para Super Admin
- Gestión de tenants
- Monitoreo de uso global
- Soporte técnico
- Configuración del sistema

## Seguridad

### Autenticación
- Firebase Authentication para usuarios
- OAuth 2.0 para Google Workspace APIs
- Tokens de acceso con expiración

### Autorización
- Sistema de roles y permisos
- Aislamiento de datos por tenant
- Verificación de permisos en cada operación

### Datos
- Encriptación en tránsito (HTTPS)
- Almacenamiento seguro en Supabase
- Backup automático en Google Drive

## Próximos Pasos de Desarrollo

1. **Configurar OAuth 2.0 Flow**
   - Implementar flujo de autenticación OAuth
   - Obtener tokens de acceso refrescables
   - Manejar expiración de tokens

2. **Mejorar OCR**
   - Entrenar modelo personalizado para facturas venezolanas
   - Mejorar precisión de extracción de datos
   - Soporte para más tipos de documentos

3. **Testing**
   - Pruebas unitarias de servicios
   - Pruebas de integración
   - Pruebas E2E

4. **Optimización**
   - Mejorar rendimiento del dashboard
   - Optimizar carga de documentos
   - Implementar caching

5. **Documentación**
   - Documentación de API
   - Guía de usuario
   - Guía de administración

## Contacto y Soporte

- **Proyecto**: (π)NAD - Sistema de Escaneo Contable
- **Fecha de Finalización**: Junio 8, 2026
- **Estado**: Completado (requiere instalación de Flutter para despliegue final)
