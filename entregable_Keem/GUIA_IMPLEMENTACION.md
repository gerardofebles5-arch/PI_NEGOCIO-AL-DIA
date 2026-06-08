# Guía de Implementación - Punto 2

## Fecha
Junio 7, 2026

## Objetivo
Implementar la aplicación web de escaneo en línea con Google Cloud, ignorando el punto 3 (agentes de IA) momentáneamente.

---

## PASO 1: Configurar Proyecto en Google Cloud Console

### 1.1 Acceder a Google Cloud Console
1. Ve a https://console.cloud.google.com
2. Inicia sesión con tu cuenta de Google Workspace
3. Si no tienes un proyecto, crea uno nuevo:
   - Haz clic en el selector de proyectos (arriba a la izquierda)
   - Haz clic en "NUEVO PROYECTO"
   - Nombre: `pinad-scanning-system`
   - Organización: Selecciona tu organización de Google Workspace
   - Haz clic en "CREAR"

### 1.2 Verificar proyecto creado
- El proyecto debería aparecer en el selector de proyectos
- Anota el ID del proyecto (generalmente es `pinad-scanning-system`)

---

## PASO 2: Habilitar APIs Necesarias

### 2.1 Habilitar APIs
1. En el menú izquierdo, ve a "API y servicios" > "Biblioteca"
2. Busca y habilita las siguientes APIs una por una:

**APIs obligatorias:**
- Cloud Firestore API
- Cloud Functions API
- Cloud Storage API
- Cloud SQL Admin API
- Document AI API
- Vertex AI API
- Cloud Pub/Sub API
- Cloud Secret Manager API
- Cloud Monitoring API

**Para habilitar una API:**
1. Busca el nombre de la API
2. Haz clic en la API
3. Haz clic en "HABILITAR"

### 2.2 Verificar APIs habilitadas
1. Ve a "API y servicios" > "APIs habilitadas"
2. Verifica que todas las APIs estén en la lista

---

## PASO 3: Configurar Firebase y Vincular con Google Cloud

### 3.1 Crear proyecto Firebase
1. Ve a https://console.firebase.google.com
2. Haz clic en "Agregar proyecto"
3. Nombre: `pinad-scanning-system`
4. Habilita Google Analytics para este proyecto (opcional pero recomendado)
5. Selecciona tu cuenta de Google Analytics o crea una nueva
6. Haz clic en "Crear proyecto"

### 3.2 Vincular Firebase con Google Cloud
Firebase se vinculará automáticamente con tu proyecto de Google Cloud si tienen el mismo nombre. Si no:

1. En Firebase Console, ve a Configuración del proyecto (icono de engranaje)
2. Ve a la pestaña "Integraciones"
3. En "Google Cloud Platform", haz clic en "Vincular"
4. Selecciona tu proyecto de Google Cloud (`pinad-scanning-system`)
5. Haz clic en "Vincular"

---

## PASO 4: Configurar Firestore Database

### 4.1 Crear base de datos Firestore
1. En Firebase Console, ve a "Firestore Database"
2. Haz clic en "Crear base de datos"
3. Selecciona una ubicación (recomendado: `us-central1` o la más cercana a tus usuarios)
4. Selecciona "Modo de producción" (para producción) o "Modo de prueba" (para desarrollo)
5. Haz clic en "Crear base de datos"

### 4.2 Configurar reglas de seguridad
1. En Firestore Database, ve a la pestaña "Reglas"
2. Reemplaza las reglas con las siguientes (para desarrollo inicial):

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

**Nota:** Estas reglas son para desarrollo. Para producción, usar las reglas multi-tenant del documento CONFIGURACION_BASE_DATOS.md

---

## PASO 5: Configurar Cloud Storage

### 5.1 Crear bucket de Cloud Storage
1. En Firebase Console, ve a "Storage"
2. Haz clic en "Comenzar"
3. Selecciona "Modo de producción" o "Modo de prueba"
4. Selecciona la misma ubicación que Firestore
5. Haz clic en "Listo"

### 5.2 Configurar reglas de seguridad
1. En Storage, ve a la pestaña "Reglas"
2. Reemplaza las reglas con las siguientes (para desarrollo inicial):

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

---

## PASO 6: Configurar Cloud SQL (PostgreSQL)

### 6.1 Crear instancia de Cloud SQL
1. En Google Cloud Console, ve a "SQL"
2. Haz clic en "Crear instancia"
3. Elige "PostgreSQL"
4. Configura:
   - ID de instancia: `pinad-postgres`
   - Contraseña de usuario: (genera una contraseña segura)
   - Versión de base de datos: PostgreSQL 15
   - Región: `us-central1` (misma que Firestore)
   - Zona: (deja la predeterminada)
5. Configura la máquina:
   - Tipo de máquina: `db-f1-micro` (para desarrollo) o `db-g1-small` (para producción)
   - Almacenamiento: 10 GB (puede crecer automáticamente)
6. Configura conexiones:
   - Nombre de conexión: `pinad-connection`
   - Habilita "Conexión privada" (opcional pero recomendado)
7. Haz clic en "Crear instancia"

**Nota:** La creación puede tardar 5-10 minutos.

### 6.2 Crear base de datos
1. Una vez creada la instancia, haz clic en ella
2. Ve a la pestaña "Bases de datos"
3. Haz clic en "Crear base de datos"
4. Nombre: `pinad_db`
5. Haz clic en "Crear"

### 6.3 Crear usuario
1. Ve a la pestaña "Usuarios"
2. Haz clic en "Agregar cuenta de usuario"
3. Nombre de usuario: `pinad_user`
4. Contraseña: (genera una contraseña segura)
5. Haz clic en "Crear"

---

## PASO 7: Configurar Document AI Processor

### 7.1 Crear procesador de Document AI
1. En Google Cloud Console, ve a "Document AI"
2. Haz clic en "Crear procesador"
3. Configura:
   - Ubicación: `us`
   - Tipo de procesador: `INVOICE_PROCESSOR` (para facturas)
   - Nombre para mostrar: `PINAD Invoice Processor`
4. Haz clic en "Crear"

### 7.2 Obtener ID del procesador
1. Una vez creado, haz clic en el procesador
2. Copia el ID del procesador (se encuentra en la URL o en la página de detalles)
3. Guárdalo para usarlo en el código

---

## PASO 8: Configurar Vertex AI

### 8.1 Habilitar Vertex AI
1. En Google Cloud Console, ve a "Vertex AI"
2. Si no está habilitado, haz clic en "Habilitar Vertex AI API"

### 8.2 Crear endpoint (opcional para producción)
1. En Vertex AI, ve a "Model Registry"
2. Para desarrollo inicial, usaremos el modelo `gemini-pro-vision` directamente sin crear endpoint personalizado

---

## PASO 9: Configurar Cloud Pub/Sub

### 9.1 Crear tema (topic)
1. En Google Cloud Console, ve a "Pub/Sub"
2. Haz clic en "Crear tema"
3. ID del tema: `document-events`
4. Haz clic en "Crear"

### 9.2 Crear suscripciones (subscriptions)
Crea las siguientes suscripciones para el tema `document-events`:

1. `ocr-subscription` - Para el agente OCR
2. `extraction-subscription` - Para el agente de extracción
3. `validation-subscription` - Para el agente de validación
4. `accounting-subscription` - Para el agente de contabilidad

**Para crear una suscripción:**
1. Haz clic en el tema `document-events`
2. Haz clic en "Crear suscripción"
3. ID de suscripción: (nombre de la suscripción)
4. Tipo de entrega: `Pull` (para Cloud Functions)
5. Haz clic en "Crear"

---

## PASO 10: Configurar Firebase Authentication

### 10.1 Habilitar métodos de autenticación
1. En Firebase Console, ve a "Authentication"
2. Haz clic en "Comenzar"
3. En la pestaña "Método de inicio de sesión", habilita:
   - Correo electrónico/contraseña
   - Google (opcional)
4. Haz clic en "Guardar"

---

## PASO 11: Configurar Firebase Hosting

### 11.1 Configurar Hosting
1. En Firebase Console, ve a "Hosting"
2. Haz clic en "Comenzar"
3. Haz clic en "Siguiente" (instalar Firebase CLI)
4. Haz clic en "Siguiente" (inicializar proyecto)
5. Configura:
   - ¿Qué quieres usar como directorio público? `build/web` (para Flutter Web)
   - ¿Quieres configurar como una aplicación de página única? Sí
6. Haz clic en "Siguiente" (implementar)
7. Haz clic en "Continuar en la consola"

---

## PASO 12: Configurar Secret Manager

### 12.1 Crear secretos
1. En Google Cloud Console, ve a "Secret Manager"
2. Haz clic en "Crear secreto"
3. Crea los siguientes secretos:

**Secreto 1: cloud-sql-credentials**
- Nombre: `cloud-sql-credentials`
- Valor (JSON):
```json
{
  "host": "IP de tu instancia Cloud SQL",
  "port": 5432,
  "database": "pinad_db",
  "user": "pinad_user",
  "password": "tu contraseña de Cloud SQL"
}
```
- Haz clic en "Crear secreto"

**Secreto 2: document-ai-processor-id**
- Nombre: `document-ai-processor-id`
- Valor: `ID del procesador de Document AI`
- Haz clic en "Crear secreto"

**Secreto 3: stripe-secret-key**
- Nombre: `stripe-secret-key`
- Valor: `sk_test_...` (clave secreta de Stripe)
- Haz clic en "Crear secreto"

---

## PASO 13: Configurar IAM y Roles

### 13.1 Crear cuenta de servicio para Cloud Functions
1. En Google Cloud Console, ve a "IAM y administrador" > "Cuentas de servicio"
2. Haz clic en "Crear cuenta de servicio"
3. Nombre: `pinad-cloud-functions`
4. Descripción: `PINAD Cloud Functions`
5. Haz clic en "Crear y continuar"
6. Roles: Agrega los siguientes roles:
   - `Cloud Functions Invoker`
   - `Cloud Functions Service Agent`
   - `Firestore User`
   - `Storage Object Admin`
   - `Document AI Processor`
   - `Vertex AI User`
   - `Cloud SQL Client`
   - `Secret Manager Secret Accessor`
   - `Pub/Sub Publisher`
   - `Pub/Sub Subscriber`
7. Haz clic en "Continuar"
8. Haz clic en "Crear cuenta de servicio"

### 13.2 Crear clave de la cuenta de servicio
1. Haz clic en la cuenta de servicio `pinad-cloud-functions`
2. Ve a la pestaña "Claves"
3. Haz clic en "Agregar clave" > "Crear clave nueva"
4. Tipo de clave: `JSON`
5. Haz clic en "Crear"
6. Descarga el archivo JSON (guárdalo en un lugar seguro)
7. **IMPORTANTE:** No compartas este archivo JSON

---

## PASO 14: Configurar gcloud CLI Localmente

### 14.1 Instalar gcloud CLI
**Windows:**
1. Descarga el instalador desde https://cloud.google.com/sdk/docs/install
2. Ejecuta el instalador
3. Sigue las instrucciones

### 14.2 Autenticar
1. Abre una terminal (PowerShell o CMD)
2. Ejecuta:
```bash
gcloud auth login
```
3. Sigue las instrucciones en el navegador

### 14.3 Configurar proyecto
```bash
gcloud config set project pinad-scanning-system
```

### 14.4 Verificar configuración
```bash
gcloud config list
```

---

## PASO 15: Configurar Firebase CLI Localmente

### 15.1 Instalar Firebase CLI
```bash
npm install -g firebase-tools
```

### 15.2 Autenticar
```bash
firebase login
```

### 15.3 Inicializar proyecto Firebase
1. Navega a tu directorio de trabajo
2. Ejecuta:
```bash
firebase init
```
3. Selecciona:
   - Functions: JavaScript o TypeScript (recomendado TypeScript)
   - Firestore: Sí
   - Hosting: Sí
   - Storage: Sí
4. Sigue las instrucciones

---

## PASO 16: Crear Estructura de Proyecto Cloud Functions

### 16.1 Crear directorio de funciones
```bash
cd functions
```

### 16.2 Instalar dependencias
```bash
npm install @google-cloud/documentai @google-cloud/vertexai @google-cloud/storage @google-cloud/firestore @google-cloud/secret-manager @google-cloud/pubsub pg firebase-admin firebase-functions
```

### 16.3 Instalar dependencias de desarrollo
```bash
npm install -D typescript @types/node
```

---

## PASO 17: Implementar Cloud Functions Básicas

### 17.1 Crear función uploadDocument
Crea el archivo `functions/src/index.ts` con el código del documento MOTOR_OCR_CLOUD_FUNCTIONS.md

### 17.2 Crear función processDocument
Agrega la función processDocument (trigger) al mismo archivo

### 17.3 Crear función getDashboardData
Agrega la función getDashboardData al mismo archivo

### 17.4 Probar localmente
```bash
firebase emulators:start
```

---

## PASO 18: Configurar Flutter Web

### 18.1 Habilitar Flutter Web
1. En tu proyecto Flutter existente, ejecuta:
```bash
flutter config --enable-web
```

### 18.2 Crear build web
```bash
flutter build web
```

### 18.3 Probar localmente
```bash
flutter run -d chrome
```

---

## PASO 19: Implementar Dashboard para Clientes

### 19.1 Crear páginas del dashboard
Usa el código del documento DASHBOARD_INTELIGENTE_CLIENTES.md para crear:
- ClientDashboardPage
- SummaryCards
- ProcessingChart
- RecentDocuments
- TransactionsTable
- AlertsPanel

### 19.2 Integrar con Firebase
1. Agrega dependencias de Firebase al pubspec.yaml
2. Configura Firebase en main.dart
3. Implementa autenticación

---

## PASO 20: Implementar Sistema Multi-tenancy

### 20.1 Implementar middleware de autenticación
Usa el código del documento SISTEMA_MULTI_TENANCY.md para crear:
- authenticateAndAuthorize
- checkTenantAccess

### 20.2 Implementar servicio de tenants
Usa el código del documento SISTEMA_MULTI_TENANCY.md para crear:
- TenantService
- Cloud Functions para gestión de tenants

### 20.3 Implementar panel de control del Tenant Admin
Usa el código del documento SISTEMA_MULTI_TENANCY.md para crear:
- TenantAdminDashboardPage
- TenantStatsCard
- ClientsList
- UpgradePlanCard

---

## PASO 21: Desplegar en Producción

### 21.1 Desplegar Cloud Functions
```bash
firebase deploy --only functions
```

### 21.2 Desplegar Firebase Hosting
```bash
firebase deploy --only hosting
```

### 21.3 Verificar despliegue
1. Ve a Firebase Console
2. Verifica que las funciones estén desplegadas
3. Verifica que el hosting esté activo
4. Abre la URL del hosting

---

## Checklist de Verificación

Antes de pasar al siguiente paso, verifica:

- [ ] Proyecto de Google Cloud creado
- [ ] Todas las APIs habilitadas
- [ ] Firebase vinculado con Google Cloud
- [ ] Firestore Database configurado
- [ ] Cloud Storage configurado
- [ ] Cloud SQL configurado y base de datos creada
- [ ] Document AI Processor creado
- [ ] Vertex AI habilitado
- [ ] Cloud Pub/Sub configurado
- [ ] Firebase Authentication configurado
- [ ] Firebase Hosting configurado
- [ ] Secret Manager configurado con secretos
- [ ] IAM y roles configurados
- [ ] gcloud CLI configurado localmente
- [ ] Firebase CLI configurado localmente
- [ ] Estructura de Cloud Functions creada
- [ ] Cloud Functions básicas implementadas
- [ ] Flutter Web configurado
- [ ] Dashboard para clientes implementado
- [ ] Sistema multi-tenancy implementado
- [ ] Desplegado en producción

---

## Tiempos Estimados

- **PASOS 1-13 (Configuración Google Cloud):** 2-3 horas
- **PASOS 14-15 (Configuración CLI):** 30 minutos
- **PASOS 16-17 (Cloud Functions):** 1-2 días
- **PASOS 18-19 (Flutter Web + Dashboard):** 2-3 días
- **PASO 20 (Multi-tenancy):** 2-3 días
- **PASO 21 (Despliegue):** 1 día

**Total estimado:** 6-10 días para implementación completa

---

## Soporte

Si encuentras algún error durante la implementación:
1. Verifica que todos los pasos anteriores estén completos
2. Revisa los logs en Google Cloud Console
3. Revisa los logs de Firebase Functions
4. Verifica que las APIs estén habilitadas
5. Verifica que los roles de IAM estén correctos

---

## Siguiente Paso

Comienza con el **PASO 1: Configurar Proyecto en Google Cloud Console** y avísame cuando lo completes para guiarte al siguiente paso.
