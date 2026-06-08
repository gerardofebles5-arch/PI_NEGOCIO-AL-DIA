# Arquitectura para Aplicación Web de Escaneo en Línea

## Fecha
Junio 7, 2026

## Objetivo
Diseñar una aplicación web que permita a los clientes escanear documentos desde el navegador, procesarlos con OCR, almacenar la información en una base de datos, y proporcionar un dashboard inteligente para visualizar la información.

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Navegador)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Flutter Web App                                          │  │
│  │  - Escaneo con cámara web                                │  │
│  │  - Dashboard para clientes                               │  │
│  │  - Visualización de documentos                           │  │
│  │  - Autenticación multi-tenant                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE CLOUD PLATFORM                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Firebase Hosting                                         │  │
│  │  - Hosting de aplicación web Flutter                     │  │
│  │  - CDN global para distribución                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud Functions (Node.js/Python)                        │  │
│  │  - uploadDocument: Subir documento a Cloud Storage       │  │
│  │  - processDocument: Procesar con Document AI             │  │
│  │  - extractData: Extraer datos con Vertex AI              │  │
│  │  - saveToDatabase: Guardar en Firestore/Cloud SQL       │  │
│  │  - getDocuments: Obtener documentos del cliente         │  │
│  │  - getDashboardData: Obtener datos del dashboard        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud Storage                                            │  │
│  │  - Almacenamiento de documentos originales               │  │
│  │  - Almacenamiento de imágenes procesadas                │  │
│  │  - Versionamiento y backup                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Firestore (NoSQL)                                         │  │
│  │  - Documentos escaneados                                  │  │
│  │  - Estados de procesamiento                               │  │
│  │  - Metadatos de documentos                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cloud SQL (PostgreSQL)                                   │  │
│  │  - Clientes y tenants                                    │  │
│  │  - Transacciones contables                               │  │
│  │  - Reportes y estados financieros                         │  │
│  │  - Historial de cambios                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document AI                                              │  │
│  │  - Procesamiento OCR de documentos                       │  │
│  │  - Extracción de campos específicos                      │  │
│  │  - Clasificación de documentos                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Vertex AI                                                │  │
│  │  - Extracción inteligente de datos                       │  │
│  │  - Clasificación de transacciones                        │  │
│  │  - Análisis de patrones                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Componentes Detallados

### 1. Frontend (Flutter Web)

#### 1.1 Configuración Flutter Web
```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_web_plugins:
    sdk: flutter
  camera: ^0.10.5+5
  image_picker: ^1.0.7
  file_picker: ^6.1.1
  firebase_core: ^2.24.2
  firebase_auth: ^4.16.0
  cloud_firestore: ^4.14.0
  cloud_functions: ^4.6.0
  cloud_storage: ^2.1.0+1
```

#### 1.2 Páginas Web
- **Landing Page**: Página de bienvenida para clientes
- **Login/Registro**: Autenticación multi-tenant
- **Dashboard Cliente**: Visualización de documentos y estados
- **Escaneo**: Captura de documentos con cámara web
- **Historial**: Historial de documentos procesados
- **Reportes**: Visualización de reportes contables

#### 1.3 Escaneo con Cámara Web
```dart
// Escaneo desde navegador
class WebScannerPage extends StatefulWidget {
  @override
  State<WebScannerPage> createState() => _WebScannerPageState();
}

class _WebScannerPageState extends State<WebScannerPage> {
  late CameraController _controller;
  bool _isScanning = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    _controller = CameraController(
      cameras[0],
      ResolutionPreset.high,
      enableAudio: false,
    );
    await _controller.initialize();
    setState(() {});
  }

  Future<void> _captureDocument() async {
    final image = await _controller.takePicture();
    await _uploadAndProcess(image);
  }
}
```

---

### 2. Backend (Cloud Functions)

#### 2.1 Función: uploadDocument
```javascript
// functions/src/uploadDocument.ts
import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import { Storage } from '@google-cloud/storage';

const storage = new Storage();
const db = admin.firestore();

export const uploadDocument = functions.https.onCall(async (data, context) => {
  const { userId, tenantId, fileData, fileName } = data;
  
  // Validar autenticación y tenant
  if (!context.auth) throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  
  // Subir a Cloud Storage
  const bucket = storage.bucket('pinad-documents');
  const file = bucket.file(`tenants/${tenantId}/users/${userId}/${fileName}`);
  
  await file.save(Buffer.from(fileData, 'base64'), {
    contentType: 'image/jpeg',
  });
  
  // Crear registro en Firestore
  const docRef = await db.collection('documents').add({
    userId,
    tenantId,
    fileName,
    storagePath: file.name,
    status: 'uploaded',
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
  });
  
  // Disparar procesamiento
  await processDocument({ documentId: docRef.id });
  
  return { documentId: docRef.id };
});
```

#### 2.2 Función: processDocument
```javascript
// functions/src/processDocument.ts
import { DocumentProcessorServiceClient } from '@google-cloud/documentai';
import { VertexAI } from '@google-cloud/vertexai';

const documentAI = new DocumentProcessorServiceClient();
const vertexAI = new VertexAI();

export const processDocument = functions.firestore
  .document('documents/{documentId}')
  .onWrite(async (change, context) => {
    const document = change.after.data();
    if (document.status !== 'uploaded') return null;
    
    // Procesar con Document AI
    const [result] = await documentAI.processDocument({
      name: `projects/${PROJECT_ID}/locations/us/processors/PROCESSOR_ID`,
      rawDocument: {
        content: await downloadFromStorage(document.storagePath),
        mimeType: 'image/jpeg',
      },
    });
    
    // Extraer datos con Vertex AI
    const extractedData = await extractDataWithVertexAI(result);
    
    // Guardar en Firestore
    await change.after.ref.update({
      status: 'processed',
      extractedData,
      processedAt: admin.firestore.FieldValue.serverTimestamp(),
    });
    
    // Guardar en Cloud SQL
    await saveToCloudSQL(document.tenantId, extractedData);
    
    return null;
  });
```

#### 2.3 Función: getDashboardData
```javascript
// functions/src/getDashboardData.ts
export const getDashboardData = functions.https.onCall(async (data, context) => {
  const { userId, tenantId } = data;
  
  if (!context.auth) throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  
  // Obtener documentos del usuario
  const documentsSnapshot = await db
    .collection('documents')
    .where('userId', '==', userId)
    .where('tenantId', '==', tenantId)
    .orderBy('createdAt', 'desc')
    .limit(50)
    .get();
  
  const documents = documentsSnapshot.docs.map(doc => doc.data());
  
  // Obtener métricas
  const metrics = await getMetrics(userId, tenantId);
  
  return { documents, metrics };
});
```

---

### 3. Base de Datos

#### 3.1 Firestore (NoSQL)

**Colección: documents**
```javascript
{
  documentId: string,
  userId: string,
  tenantId: string,
  fileName: string,
  storagePath: string,
  status: 'uploaded' | 'processing' | 'processed' | 'failed',
  extractedData: {
    invoiceNumber: string,
    date: string,
    amount: number,
    taxAmount: number,
    vendor: string,
    items: Array<{name: string, quantity: number, price: number}>,
  },
  createdAt: Timestamp,
  processedAt: Timestamp,
}
```

**Colección: tenants**
```javascript
{
  tenantId: string,
  name: string,
  plan: 'basic' | 'pro' | 'enterprise',
  maxUsers: number,
  createdAt: Timestamp,
}
```

**Colección: users**
```javascript
{
  userId: string,
  tenantId: string,
  email: string,
  role: 'admin' | 'client' | 'viewer',
  createdAt: Timestamp,
}
```

#### 3.2 Cloud SQL (PostgreSQL)

**Tabla: clients**
```sql
CREATE TABLE clients (
  client_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  rif VARCHAR(50),
  email VARCHAR(255),
  phone VARCHAR(50),
  address TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);
```

**Tabla: transactions**
```sql
CREATE TABLE transactions (
  transaction_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  document_id VARCHAR(255),
  client_id INTEGER,
  type VARCHAR(50) NOT NULL, -- 'income' | 'expense'
  amount DECIMAL(15, 2) NOT NULL,
  tax_amount DECIMAL(15, 2),
  date DATE NOT NULL,
  description TEXT,
  category VARCHAR(100),
  status VARCHAR(50) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
  FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
```

**Tabla: audit_log**
```sql
CREATE TABLE audit_log (
  log_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  user_id VARCHAR(255) NOT NULL,
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(100),
  entity_id VARCHAR(255),
  old_data JSONB,
  new_data JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);
```

---

### 4. Multi-tenancy

#### 4.1 Arquitectura Multi-tenant
- **Tenant Isolation**: Cada contador es un tenant independiente
- **Data Isolation**: Todos los datos incluyen tenant_id
- **Role-based Access Control**: Admin, Client, Viewer
- **Resource Limits**: Límites por plan (basic, pro, enterprise)

#### 4.2 Implementación de Roles
```dart
// Middleware de autenticación y autorización
class AuthMiddleware {
  static Future<bool> checkPermission(
    String userId,
    String tenantId,
    String requiredRole,
  ) async {
    final userDoc = await FirebaseFirestore.instance
      .collection('users')
      .doc(userId)
      .get();
    
    final userData = userDoc.data() as Map<String, dynamic>;
    
    if (userData['tenantId'] != tenantId) return false;
    
    final role = userData['role'] as String;
    final roleHierarchy = {'viewer': 1, 'client': 2, 'admin': 3};
    
    return roleHierarchy[role]! >= roleHierarchy[requiredRole]!;
  }
}
```

---

### 5. Dashboard Inteligente para Clientes

#### 5.1 Componentes del Dashboard
- **Resumen de Documentos**: Total de documentos, estados, últimos 7 días
- **Documentos Recientes**: Lista de documentos procesados recientemente
- **Estados de Procesamiento**: Gráfico de estados (uploaded, processing, processed, failed)
- **Transacciones Extraídas**: Tabla de transacciones extraídas de documentos
- **Alertas**: Notificaciones de documentos fallidos o pendientes
- **Exportación**: Exportar datos a CSV, PDF

#### 5.2 Implementación del Dashboard
```dart
class ClientDashboardPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Dashboard')),
      body: BlocBuilder<DashboardCubit, DashboardState>(
        builder: (context, state) {
          if (state is DashboardLoading) {
            return CircularProgressIndicator();
          } else if (state is DashboardLoaded) {
            return SingleChildScrollView(
              child: Column(
                children: [
                  _SummaryCards(metrics: state.metrics),
                  _RecentDocuments(documents: state.documents),
                  _ProcessingChart(status: state.status),
                  _ExtractedTransactions(transactions: state.transactions),
                ],
              ),
            );
          }
          return SizedBox.shrink();
        },
      ),
    );
  }
}
```

---

### 6. Retención y Recuperación de Datos

#### 6.1 Sistema de Archivado
- **Periodos**: 2-3 días para procesamiento, luego archivado
- **Cold Storage**: Mover documentos antiguos a Cold Storage
- **Backup Automático**: Backup diario de Firestore y Cloud SQL
- **Retrieval**: Sistema de recuperación de datos históricos

#### 6.2 Implementación de Archivado
```javascript
// Cloud Function para archivar documentos
export const archiveOldDocuments = functions.pubsub
  .schedule('0 2 * * *') // Ejecutar diariamente a las 2 AM
  .onRun(async (context) => {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 3); // 3 días atrás
    
    const oldDocs = await db
      .collection('documents')
      .where('createdAt', '<', cutoffDate)
      .where('status', '==', 'processed')
      .get();
    
    for (const doc of oldDocs.docs) {
      // Mover a Cold Storage
      await moveToColdStorage(doc.data().storagePath);
      
      // Actualizar estado
      await doc.ref.update({ status: 'archived' });
    }
  });
```

---

## Pasos de Implementación

### Fase 1: Configuración Base (1-2 semanas)
1. Configurar Flutter Web
2. Configurar Firebase Hosting
3. Configurar Cloud Storage
4. Configurar Firestore
5. Configurar Cloud SQL

### Fase 2: Backend (2-3 semanas)
1. Implementar Cloud Functions
2. Integrar Document AI
3. Integrar Vertex AI
4. Implementar multi-tenancy
5. Implementar sistema de roles

### Fase 3: Frontend (2-3 semanas)
1. Implementar escaneo con cámara web
2. Implementar dashboard para clientes
3. Implementar autenticación multi-tenant
4. Implementar visualización de documentos
5. Implementar exportación de datos

### Fase 4: Testing y Despliegue (1-2 semanas)
1. Testing unitario
2. Testing de integración
3. Testing E2E
4. Despliegue en Google Cloud
5. Configurar monitoreo y alertas

---

## Estimación de Tiempo Total
**6-10 semanas** para completar la aplicación web de escaneo en línea con dashboard inteligente y multi-tenancy.
